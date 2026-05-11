"""Drama Subtext Model — Training Pipeline (P6).

Trains a multi-label classifier that maps scene context to subtext labels,
replacing the rule-based ``SubtextEngine`` heuristic with a learned model.

Usage
-----
1.  Populate ``drama_subtext_labels`` with scene context features and
    human-annotated subtext label vectors::

        INSERT INTO drama_subtext_labels
            (scene_id, denial_score, deflection_score, sarcasm_score,
             suppression_score, manipulation_score, vulnerability_score,
             power_play_score, irony_score, scene_tension_score,
             power_imbalance_score, truth_score,
             -- target labels (one-hot / multi-label):
             denial_label, deflection_label, sarcasm_label, suppression_label,
             vulnerability_exposure_label)
        SELECT ... FROM drama_scenes ...;

2.  Run this script::

        python -m app.ml.training.drama_subtext_trainer \
            --artifact-dir /artifacts/models/drama_subtext \
            --min-samples 400

3.  Set the env var and restart::

        DRAMA_SUBTEXT_MODEL_PATH=/artifacts/models/drama_subtext/latest.joblib

4.  Confirm ``subtext_engine_placeholder`` Prometheus metric drops to 0.

Feature vector (11 dimensions)
-------------------------------
denial_score, deflection_score, sarcasm_score, suppression_score,
manipulation_score, vulnerability_score, power_play_score, irony_score,
scene_tension_score, power_imbalance_score, truth_score

Labels (5 binary)
------------------
denial, deflection, sarcasm, suppression, vulnerability_exposure
(multi-label; model outputs independent probabilities per label)
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
    "denial_score",
    "deflection_score",
    "sarcasm_score",
    "suppression_score",
    "manipulation_score",
    "vulnerability_score",
    "power_play_score",
    "irony_score",
    "scene_tension_score",
    "power_imbalance_score",
    "truth_score",
]

_LABEL_COLUMNS = [
    "denial_label",
    "deflection_label",
    "sarcasm_label",
    "suppression_label",
    "vulnerability_exposure_label",
]

_DEFAULT_ARTIFACT_DIR = "/artifacts/models/drama_subtext"
_MIN_SAMPLES_DEFAULT = 400


def _fetch_training_data(db_url: str) -> tuple[list[list[float]], list[list[int]]]:
    from sqlalchemy import create_engine, text  # noqa: PLC0415

    # Validate column names against the known allowlist before embedding in SQL.
    _ALLOWED_COLUMNS: frozenset[str] = frozenset(_FEATURE_COLUMNS) | frozenset(_LABEL_COLUMNS) | {"created_at"}
    for col in _FEATURE_COLUMNS + _LABEL_COLUMNS:
        if not col.replace("_", "").isalnum() or col not in _ALLOWED_COLUMNS:
            raise ValueError(f"Unsafe column name rejected: {col!r}")

    all_cols = ", ".join(_FEATURE_COLUMNS + _LABEL_COLUMNS)
    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                f"SELECT {all_cols} FROM drama_subtext_labels "
                "WHERE denial_label IS NOT NULL "
                "ORDER BY created_at DESC"
            )
        ).fetchall()

    X = [[float(getattr(row, col)) for col in _FEATURE_COLUMNS] for row in rows]
    y = [[int(getattr(row, col)) for col in _LABEL_COLUMNS] for row in rows]
    return X, y


def _generate_synthetic_data(n: int = 800) -> tuple[list[list[float]], list[list[int]]]:
    import random  # noqa: PLC0415

    rng = random.Random(7)
    X, y = [], []
    for _ in range(n):
        feats = [rng.uniform(0, 10) for _ in _FEATURE_COLUMNS]
        labels = [
            1 if feats[0] > 6.5 else 0,        # denial
            1 if feats[1] > 6.5 else 0,        # deflection
            1 if feats[2] > 7.0 else 0,        # sarcasm
            1 if feats[3] > 6.5 else 0,        # suppression
            1 if feats[5] > 7.0 else 0,        # vulnerability_exposure
        ]
        X.append(feats)
        y.append(labels)
    return X, y


def train(
    artifact_dir: str = _DEFAULT_ARTIFACT_DIR,
    db_url: str | None = None,
    min_samples: int = _MIN_SAMPLES_DEFAULT,
    synthetic_fallback: bool = False,
) -> dict[str, Any]:
    """Train and save the subtext multi-label classifier.

    Returns a dict with training metrics and the artifact path.
    """
    import joblib  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    from sklearn.ensemble import GradientBoostingClassifier  # noqa: PLC0415
    from sklearn.metrics import f1_score  # noqa: PLC0415
    from sklearn.model_selection import train_test_split  # noqa: PLC0415
    from sklearn.multioutput import MultiOutputClassifier  # noqa: PLC0415

    db_url = db_url or os.getenv("DATABASE_URL", "")

    X: list[list[float]]
    y: list[list[int]]
    data_source: str

    if db_url:
        try:
            X, y = _fetch_training_data(db_url)
            data_source = "database"
        except Exception as exc:  # noqa: BLE001
            _logger.warning("DB fetch failed (%s); using synthetic data.", exc)
            X, y = [], []
            data_source = "synthetic"
    else:
        X, y = [], []
        data_source = "synthetic"

    if len(X) < min_samples:
        if not synthetic_fallback:
            raise RuntimeError(
                f"Only {len(X)} labelled samples found (min={min_samples}). "
                "Populate drama_subtext_labels before training."
            )
        _logger.warning(
            "Only %d labelled samples (min=%d). Falling back to synthetic data.",
            len(X), min_samples,
        )
        X, y = _generate_synthetic_data(800)
        data_source = "synthetic"

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.int32)
    X_train, X_test, y_train, y_test = train_test_split(X_arr, y_arr, test_size=0.2, random_state=42)

    base_clf = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    model = MultiOutputClassifier(base_clf)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))

    out_dir = Path(artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = str(out_dir / "latest.joblib")
    joblib.dump(model, artifact_path)

    metrics = {
        "n_samples": len(X),
        "test_macro_f1": round(macro_f1, 4),
        "data_source": data_source,
        "artifact_path": artifact_path,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": _FEATURE_COLUMNS,
        "label_columns": _LABEL_COLUMNS,
        "next_step": (
            "Set DRAMA_SUBTEXT_MODEL_PATH=" + artifact_path
            + " and restart. Confirm subtext_engine_placeholder drops to 0."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    _logger.info(
        "drama_subtext_trainer: saved to %s (macro_f1=%.4f, n=%d, source=%s)",
        artifact_path, macro_f1, len(X), data_source,
    )
    return metrics


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Train the drama subtext classifier.")
    parser.add_argument("--artifact-dir", default=_DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--db-url", default=None)
    parser.add_argument("--min-samples", type=int, default=_MIN_SAMPLES_DEFAULT)
    parser.add_argument("--no-synthetic-fallback", action="store_true")
    args = parser.parse_args()
    synthetic_fallback = cli_synthetic_fallback_enabled(
        no_synthetic_fallback=args.no_synthetic_fallback
    )
    print(json.dumps(train(
        artifact_dir=args.artifact_dir,
        db_url=args.db_url,
        min_samples=args.min_samples,
        synthetic_fallback=synthetic_fallback,
    ), indent=2))


if __name__ == "__main__":
    main()
