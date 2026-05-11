"""Drama Character Intent Model — Training Pipeline (P6).

Trains a gradient-boosted regression model that predicts scene-level character
intent as a score ∈ [0, 1] which maps to one of six intent labels via the
``_INTENT_LABELS`` index in ``CharacterIntentEngine``.

Usage
-----
1.  Populate ``drama_character_intent_labels`` with (character, scene) pairs
    and a human-annotated ``intent_label_idx`` ∈ [0, 5]::

        INSERT INTO drama_character_intent_labels
            (character_id, scene_id, has_outer_goal, has_beat_goal,
             has_hidden_need, has_dominant_fear, has_mask_strategy,
             exposure_risk, intent_label_idx)
        SELECT ... FROM drama_characters JOIN drama_scenes ...;

    Intent label indices map to::

        0 → advance_outer_goal
        1 → pursue_scene_goal
        2 → protect_self_position
        3 → exploit_vulnerability
        4 → seek_validation
        5 → deflect_threat

2.  Run this script::

        python -m app.ml.training.drama_character_intent_trainer \\
            --artifact-dir /artifacts/models/drama_intent \\
            --min-samples 300

3.  Set the env var and restart::

        DRAMA_INTENT_MODEL_PATH=/artifacts/models/drama_intent/latest.joblib

4.  Confirm ``character_intent_engine_placeholder`` Prometheus metric drops to 0.

Feature vector (6 dimensions)
------------------------------
+---+------------------------+-----------------------------------------------+
| 0 | has_outer_goal         | 1.0 if character has an outer goal            |
| 1 | has_beat_goal          | 1.0 if scene has a beat-level goal            |
| 2 | has_hidden_need        | 1.0 if character has a hidden need            |
| 3 | has_dominant_fear      | 1.0 if character has a dominant fear          |
| 4 | has_mask_strategy      | 1.0 if character uses a mask strategy         |
| 5 | exposure_risk          | scene exposure_risk ∈ [0, 1]                  |
+---+------------------------+-----------------------------------------------+

Label
-----
``intent_label_idx`` ∈ [0, 5] (integer class index).  The trainer normalises
to [0, 1] so ``predict_from_artifact()`` returns values in the expected range,
and ``CharacterIntentEngine._try_model_intent()`` maps back to a label string.
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
    "has_outer_goal",
    "has_beat_goal",
    "has_hidden_need",
    "has_dominant_fear",
    "has_mask_strategy",
    "exposure_risk",
]

_LABEL_COLUMN = "intent_label_idx"
_NUM_LABELS = 6
_DEFAULT_ARTIFACT_DIR = "/artifacts/models/drama_intent"
_MIN_SAMPLES_DEFAULT = 300


def _fetch_training_data(db_url: str) -> tuple[list[list[float]], list[float]]:
    """Fetch feature vectors and labels from the DB.

    Returns ``(X, y)`` where both are plain Python lists.
    """
    from sqlalchemy import create_engine, text  # noqa: PLC0415

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
                "FROM drama_character_intent_labels "
                "WHERE intent_label_idx IS NOT NULL "
                "ORDER BY created_at DESC"
            )
        ).fetchall()

    X = [[float(getattr(row, col)) for col in _FEATURE_COLUMNS] for row in rows]
    # Normalise label index to [0, 1] for regression compatibility.
    y = [float(getattr(row, _LABEL_COLUMN)) / float(_NUM_LABELS - 1) for row in rows]
    return X, y


def _generate_synthetic_data(n: int = 500) -> tuple[list[list[float]], list[float]]:
    """Generate synthetic training data for CI/dev validation of the pipeline.

    Not suitable for production use — replace with real labelled data.
    """
    import random  # noqa: PLC0415

    rng = random.Random(42)
    X, y = [], []
    for _ in range(n):
        has_outer_goal = float(rng.choice([0.0, 1.0]))
        has_beat_goal = float(rng.choice([0.0, 1.0]))
        has_hidden_need = float(rng.choice([0.0, 1.0]))
        has_dominant_fear = float(rng.choice([0.0, 1.0]))
        has_mask_strategy = float(rng.choice([0.0, 1.0]))
        exposure_risk = rng.uniform(0.0, 1.0)
        # Synthetic rule: map feature combinations to label indices.
        if has_outer_goal and has_beat_goal:
            label_idx = 1  # pursue_scene_goal
        elif has_outer_goal:
            label_idx = 0  # advance_outer_goal
        elif has_dominant_fear and exposure_risk > 0.6:
            label_idx = 5  # deflect_threat
        elif has_hidden_need:
            label_idx = 4  # seek_validation
        elif has_mask_strategy:
            label_idx = 3  # exploit_vulnerability
        else:
            label_idx = 2  # protect_self_position
        X.append([has_outer_goal, has_beat_goal, has_hidden_need, has_dominant_fear, has_mask_strategy, exposure_risk])
        y.append(float(label_idx) / float(_NUM_LABELS - 1))
    return X, y


def train(
    artifact_dir: str = _DEFAULT_ARTIFACT_DIR,
    db_url: str | None = None,
    min_samples: int = _MIN_SAMPLES_DEFAULT,
    synthetic_fallback: bool = False,
) -> dict[str, Any]:
    """Train the drama character intent model and save the artifact.

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
                "Populate drama_character_intent_labels before training."
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
        max_depth=3,
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
    joblib.dump(model, artifact_path)

    metrics = {
        "n_samples": len(X),
        "test_rmse": round(rmse, 4),
        "data_source": data_source,
        "artifact_path": artifact_path,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": _FEATURE_COLUMNS,
        "label_column": _LABEL_COLUMN,
        "label_scale": f"intent_label_idx / {_NUM_LABELS - 1} → [0, 1]",
        "num_labels": _NUM_LABELS,
        "label_map": {
            "0": "advance_outer_goal",
            "1": "pursue_scene_goal",
            "2": "protect_self_position",
            "3": "exploit_vulnerability",
            "4": "seek_validation",
            "5": "deflect_threat",
        },
        "next_step": (
            "Set DRAMA_INTENT_MODEL_PATH=" + artifact_path
            + " and restart API workers to activate. "
            "Confirm Prometheus character_intent_engine_placeholder drops to 0."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    _logger.info(
        "drama_character_intent_trainer: saved artifact to %s (RMSE=%.4f, n=%d, source=%s)",
        artifact_path,
        rmse,
        len(X),
        data_source,
    )
    return metrics


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Train the drama character intent model.")
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
