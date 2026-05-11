"""Drama Memory Recall Model — Training Pipeline (P6).

Trains a relevance-ranking model for the ``MemoryRecallEngine``.  The model
predicts how relevant a stored memory is for a given trigger text, replacing
the heuristic word-boundary scoring with a learned ranking function.

Usage
-----
1.  Populate ``drama_memory_recall_labels`` with (trigger, memory) pairs and
    a human-annotated ``relevance_score`` ∈ [0, 1]::

        INSERT INTO drama_memory_recall_labels
            (trigger_text, recall_trigger, meaning_label,
             persistence_score, emotional_weight, relevance_score)
        SELECT ... FROM drama_memories JOIN drama_episodes ...;

2.  Run this script::

        python -m app.ml.training.drama_memory_recall_trainer \
            --artifact-dir /artifacts/models/drama_memory_recall \
            --min-samples 300

3.  Set the env var and restart::

        DRAMA_MEMORY_RECALL_MODEL_PATH=/artifacts/models/drama_memory_recall/latest.joblib

4.  Confirm ``memory_recall_engine_placeholder`` Prometheus metric drops to 0.

Feature vector (5 dimensions)
------------------------------
+---+-------------------------------+------------------------------------+
| 0 | trigger_in_recall             | 1.0 if word-boundary match else 0  |
| 1 | trigger_in_meaning            | 1.0 if word-boundary match else 0  |
| 2 | persistence_score             | raw persistence_score from DB      |
| 3 | emotional_weight              | clamped to [0, 1]                  |
| 4 | trigger_len_norm              | len(trigger) / 50.0 (capped at 1)  |
+---+-------------------------------+------------------------------------+

Label
-----
``relevance_score`` ∈ [0, 1].
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.ml.training._runtime_policy import cli_synthetic_fallback_enabled

_logger = logging.getLogger(__name__)

_FEATURE_COLUMNS = [
    "trigger_in_recall",
    "trigger_in_meaning",
    "persistence_score",
    "emotional_weight",
    "trigger_len_norm",
]

_LABEL_COLUMN = "relevance_score"
_DEFAULT_ARTIFACT_DIR = "/artifacts/models/drama_memory_recall"
_MIN_SAMPLES_DEFAULT = 300


def _word_boundary_match(trigger: str, text: str) -> float:
    """Return 1.0 if trigger matches at a word boundary in text, 0.5 for substring, else 0.0."""
    if not trigger or not text:
        return 0.0
    escaped = re.escape(trigger.lower())
    if re.search(rf"\b{escaped}\b", text.lower()):
        return 1.0
    if trigger.lower() in text.lower():
        return 0.5
    return 0.0


def _row_to_features(row: Any) -> list[float]:
    trigger = str(getattr(row, "trigger_text", "") or "").strip().lower()
    recall = str(getattr(row, "recall_trigger", "") or "").lower()
    meaning = str(getattr(row, "meaning_label", "") or "").lower()
    persistence = float(getattr(row, "persistence_score", 0.0) or 0.0)
    emotional = min(float(getattr(row, "emotional_weight", 0.0) or 0.0), 1.0)
    tlen = min(len(trigger) / 50.0, 1.0)
    return [
        _word_boundary_match(trigger, recall),
        _word_boundary_match(trigger, meaning),
        persistence,
        emotional,
        tlen,
    ]


def _fetch_training_data(db_url: str) -> tuple[list[list[float]], list[float]]:
    from sqlalchemy import create_engine, text  # noqa: PLC0415

    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT trigger_text, recall_trigger, meaning_label, "
                "persistence_score, emotional_weight, relevance_score "
                "FROM drama_memory_recall_labels "
                "WHERE relevance_score IS NOT NULL "
                "ORDER BY created_at DESC"
            )
        ).fetchall()
    X = [_row_to_features(row) for row in rows]
    y = [float(getattr(row, _LABEL_COLUMN)) for row in rows]
    return X, y


def _generate_synthetic_data(n: int = 600) -> tuple[list[list[float]], list[float]]:
    import random  # noqa: PLC0415

    rng = random.Random(99)
    X, y = [], []
    for _ in range(n):
        t_recall = float(rng.choice([0.0, 0.5, 1.0]))
        t_meaning = float(rng.choice([0.0, 0.5, 1.0]))
        persistence = rng.uniform(0, 1)
        emotional = rng.uniform(0, 1)
        tlen = rng.uniform(0, 1)
        label = min(1.0, t_recall * 0.45 + persistence * 0.35 + emotional * 0.20 + rng.uniform(-0.05, 0.05))
        label = max(0.0, label)
        X.append([t_recall, t_meaning, persistence, emotional, tlen])
        y.append(label)
    return X, y


def train(
    artifact_dir: str = _DEFAULT_ARTIFACT_DIR,
    db_url: str | None = None,
    min_samples: int = _MIN_SAMPLES_DEFAULT,
    synthetic_fallback: bool = False,
) -> dict[str, Any]:
    """Train and save the memory recall relevance model."""
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
                "Populate drama_memory_recall_labels before training."
            )
        _logger.warning(
            "Only %d labelled samples (min=%d). Falling back to synthetic data.",
            len(X), min_samples,
        )
        X, y = _generate_synthetic_data(600)
        data_source = "synthetic"

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.float32)
    X_train, X_test, y_train, y_test = train_test_split(X_arr, y_arr, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.08, random_state=42)
    model.fit(X_train, y_train)
    rmse = float(np.sqrt(mean_squared_error(y_test, model.predict(X_test))))

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
        "next_step": (
            "Set DRAMA_MEMORY_RECALL_MODEL_PATH=" + artifact_path
            + " and restart. Confirm memory_recall_engine_placeholder drops to 0."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    _logger.info(
        "drama_memory_recall_trainer: saved to %s (RMSE=%.4f, n=%d, source=%s)",
        artifact_path, rmse, len(X), data_source,
    )
    return metrics


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Train the memory recall relevance model.")
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
