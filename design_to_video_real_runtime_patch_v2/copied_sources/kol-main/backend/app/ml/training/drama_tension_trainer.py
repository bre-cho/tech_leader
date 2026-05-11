"""Drama Tension Model — Training Pipeline (P6).

Trains a gradient-boosted regression model that predicts scene-level tension
scores (∈ [0, 1], scaled from the heuristic [0, 100] range) from per-scene
features stored in the ``drama_scene_tension_labels`` table.

Usage
-----
1.  Populate ``drama_scene_tension_labels`` by running heuristic scoring on
    historical scenes and having human editors annotate/correct the scores::

        # One-shot backfill — run in a migration or admin endpoint:
        INSERT INTO drama_scene_tension_labels
            (scene_id, intent_count, relationship_count, hidden_agenda_sum,
             dominance_sum, exposure_risk, unresolved_prior_memory,
             time_pressure, social_consequence, tension_score_label, source)
        SELECT ... FROM drama_scenes JOIN drama_relationships ...;

2.  Run this script::

        python -m app.ml.training.drama_tension_trainer \
            --artifact-dir /artifacts/models/drama_tension \
            --min-samples 200

3.  Verify the saved artifact::

        python -c "
        import joblib, numpy as np
        m = joblib.load('/artifacts/models/drama_tension/latest.joblib')
        print(m.predict(np.array([[3,2,4.5,3.0,8.0,6.0,5.0,6.0]])))
        "

4.  Set the env var and restart the API worker::

        DRAMA_TENSION_MODEL_PATH=/artifacts/models/drama_tension/latest.joblib

5.  Confirm the Prometheus metric ``tension_engine_placeholder`` drops to 0
    after the first scored scene reaches the engine.

Feature vector (8 dimensions)
------------------------------
+---+-------------------------------+----------------------------------+
| 0 | intent_count                  | number of character intents      |
| 1 | relationship_count            | relationship snapshots in scene  |
| 2 | hidden_agenda_sum             | sum of hidden_agenda_score vals  |
| 3 | dominance_sum                 | sum of abs(dominance) deltas     |
| 4 | exposure_risk                 | scene_context exposure_risk      |
| 5 | unresolved_prior_memory       | scene_context unresolved memory  |
| 6 | time_pressure                 | scene_context time_pressure      |
| 7 | social_consequence            | scene_context social_consequence |
+---+-------------------------------+----------------------------------+

Label
-----
``tension_score_label`` ∈ [0, 100] as stored in the DB.  The trainer rescales
to [0, 1] so ``predict_from_artifact()`` in ml/serving.py returns values in
the expected range, and ``TensionEngine._try_model_score()`` multiplies back
by 100 before returning.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.ml.training._runtime_policy import cli_synthetic_fallback_enabled

_logger = logging.getLogger(__name__)

_FEATURE_COLUMNS = [
    "intent_count",
    "relationship_count",
    "hidden_agenda_sum",
    "dominance_sum",
    "exposure_risk",
    "unresolved_prior_memory",
    "time_pressure",
    "social_consequence",
]

_LABEL_COLUMN = "tension_score_label"
_DEFAULT_ARTIFACT_DIR = "/artifacts/models/drama_tension"
_MIN_SAMPLES_DEFAULT = 200


def _fetch_training_data(db_url: str) -> tuple[list[list[float]], list[float]]:
    """Fetch feature vectors and labels from the DB.

    Returns ``(X, y)`` where both are plain Python lists.
    """
    from sqlalchemy import create_engine, text  # noqa: PLC0415

    # Validate column names against the known allowlist before embedding in SQL
    # to prevent injection if _FEATURE_COLUMNS or _LABEL_COLUMN are ever made
    # dynamic (e.g. loaded from config).
    _ALLOWED_COLUMNS: frozenset[str] = frozenset(_FEATURE_COLUMNS) | {_LABEL_COLUMN, "created_at"}
    for col in _FEATURE_COLUMNS + [_LABEL_COLUMN]:
        if not col.replace("_", "").isalnum() or col not in _ALLOWED_COLUMNS:
            raise ValueError(f"Unsafe column name rejected: {col!r}")

    col_list = ", ".join(_FEATURE_COLUMNS + [_LABEL_COLUMN])

    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                f"SELECT {col_list} "
                "FROM drama_scene_tension_labels "
                "WHERE tension_score_label IS NOT NULL "
                "ORDER BY created_at DESC"
            )
        ).fetchall()

    X = [[float(getattr(row, col)) for col in _FEATURE_COLUMNS] for row in rows]
    y = [float(getattr(row, _LABEL_COLUMN)) / 100.0 for row in rows]  # scale to [0,1]
    return X, y


def _generate_synthetic_data(n: int = 500) -> tuple[list[list[float]], list[float]]:
    """Generate synthetic training data for CI/dev validation of the pipeline.

    Not suitable for production use — replace with real labelled data.
    """
    import random  # noqa: PLC0415

    rng = random.Random(42)
    X, y = [], []
    for _ in range(n):
        intents = rng.randint(1, 6)
        rels = rng.randint(1, 4)
        ha = rng.uniform(0, 15)
        dom = rng.uniform(0, 10)
        exp = rng.uniform(2, 20)
        mem = rng.uniform(2, 15)
        tp = rng.uniform(1, 15)
        sc = rng.uniform(1, 15)
        # Synthetic label: rough linear combination scaled to [0,1]
        raw = intents * 8 + ha * 0.5 + dom * 0.4 + exp + mem + tp + sc
        label = min(1.0, raw / 100.0)
        X.append([float(intents), float(rels), ha, dom, exp, mem, tp, sc])
        y.append(label)
    return X, y


def train(
    artifact_dir: str = _DEFAULT_ARTIFACT_DIR,
    db_url: str | None = None,
    min_samples: int = _MIN_SAMPLES_DEFAULT,
    synthetic_fallback: bool = False,
) -> dict[str, Any]:
    """Train the drama tension model and save the artifact.

    Parameters
    ----------
    artifact_dir:
        Directory to write ``latest.joblib`` and ``metrics.json``.
    db_url:
        SQLAlchemy database URL.  Defaults to ``DATABASE_URL`` env var.
    min_samples:
        Minimum number of labelled samples required to proceed with real data.
        Falls back to synthetic data when fewer samples are available.
    synthetic_fallback:
        When ``True``, fall back to synthetic data if the DB has fewer than
        ``min_samples`` rows.  Set to ``False`` in production to fail hard.

    Returns
    -------
    dict
        Training metrics: ``n_samples``, ``test_rmse``, ``artifact_path``.
    """
    import joblib  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    from sklearn.ensemble import GradientBoostingRegressor  # noqa: PLC0415
    from sklearn.metrics import mean_squared_error  # noqa: PLC0415
    from sklearn.model_selection import train_test_split  # noqa: PLC0415

    db_url = db_url or os.getenv("DATABASE_URL", "")

    X: list[list[float]]
    y: list[float]
    data_source: str

    if db_url:
        try:
            X, y = _fetch_training_data(db_url)
            data_source = "database"
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Failed to fetch training data from DB (%s); using synthetic data.", exc)
            X, y = [], []
            data_source = "synthetic"
    else:
        X, y = [], []
        data_source = "synthetic"

    if len(X) < min_samples:
        if not synthetic_fallback:
            raise RuntimeError(
                f"Only {len(X)} labelled samples found (min={min_samples}). "
                "Populate drama_scene_tension_labels before training."
            )
        _logger.warning(
            "Only %d labelled samples available (min=%d). "
            "Falling back to synthetic data — NOT suitable for production.",
            len(X),
            min_samples,
        )
        X, y = _generate_synthetic_data(500)
        data_source = "synthetic"

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.float32)
    X_train, X_test, y_train, y_test = train_test_split(X_arr, y_arr, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    out_dir = Path(artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = str(out_dir / "latest.joblib")
    bundle = {
        "__schema_version__": "tension_v1",
        "__model__": model,
        "__feature_schema__": _FEATURE_COLUMNS,
        "__label_column__": _LABEL_COLUMN,
    }
    joblib.dump(bundle, artifact_path)

    metrics = {
        "n_samples": len(X),
        "test_rmse": round(rmse, 4),
        "data_source": data_source,
        "artifact_path": artifact_path,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": _FEATURE_COLUMNS,
        "label_column": _LABEL_COLUMN,
        "label_scale": "tension_score / 100.0 → [0, 1]",
        "next_step": (
            "Set DRAMA_TENSION_MODEL_PATH=" + artifact_path
            + " and restart API workers to activate. "
            "Confirm Prometheus tension_engine_placeholder drops to 0."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    _logger.info(
        "drama_tension_trainer: saved artifact to %s (RMSE=%.4f, n=%d, source=%s)",
        artifact_path,
        rmse,
        len(X),
        data_source,
    )
    return metrics


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Train the drama tension model.")
    parser.add_argument("--artifact-dir", default=_DEFAULT_ARTIFACT_DIR, help="Output artifact directory")
    parser.add_argument("--db-url", default=None, help="SQLAlchemy DB URL (defaults to DATABASE_URL env var)")
    parser.add_argument("--min-samples", type=int, default=_MIN_SAMPLES_DEFAULT, help="Min labelled rows required")
    parser.add_argument(
        "--no-synthetic-fallback",
        action="store_true",
        help="Fail if not enough real samples (forced on in production/staging)",
    )
    args = parser.parse_args()
    synthetic_fallback = cli_synthetic_fallback_enabled(
        no_synthetic_fallback=args.no_synthetic_fallback
    )

    metrics = train(
        artifact_dir=args.artifact_dir,
        db_url=args.db_url,
        min_samples=args.min_samples,
        synthetic_fallback=synthetic_fallback,
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
