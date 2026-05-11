from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import numpy as np  # type: ignore
except Exception:  # noqa: BLE001
    np = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # noqa: BLE001
    pd = None  # type: ignore


JOB_FEATURE_COLS: list[str] = [
    "planned_scene_count",
    "completed_scene_count",
    "failed_scene_count",
    "duration_seconds",
    "retry_count",
]


def _to_dataframe(rows: list[dict[str, Any]]):
    if pd is None:
        return rows
    return pd.DataFrame(rows)


def _iter_rows(df: Any) -> list[dict[str, Any]]:
    if pd is not None and isinstance(df, pd.DataFrame):
        return [dict(row) for row in df.to_dict(orient="records")]
    if isinstance(df, list):
        return [dict(item or {}) for item in df]
    return []


def load_jobs_dataframe(db: Any, *, lookback_days: int = 30):
    rows: list[dict[str, Any]] = []
    if db is not None:
        try:
            from sqlalchemy import text  # noqa: PLC0415

            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=max(1, int(lookback_days)))
            query = text(
                "SELECT planned_scene_count, completed_scene_count, failed_scene_count, "
                "duration_seconds, retry_count "
                "FROM render_jobs "
                "WHERE created_at >= :cutoff"
            )
            for row in db.execute(query, {"cutoff": cutoff}).mappings().all():
                rows.append(dict(row))
        except Exception:  # noqa: BLE001
            rows = []
    return _to_dataframe(rows)


def build_job_features(df: Any):
    rows = _iter_rows(df)
    if not rows:
        return _to_dataframe([])

    out_rows: list[dict[str, Any]] = []
    for row in rows:
        normalized: dict[str, Any] = {}
        for col in JOB_FEATURE_COLS:
            try:
                normalized[col] = float(row.get(col, 0.0) or 0.0)
            except (TypeError, ValueError):
                normalized[col] = 0.0
        planned = normalized["planned_scene_count"] or 0.0
        fail_ratio = 0.0 if planned <= 0 else normalized["failed_scene_count"] / planned
        normalized["fail_ratio"] = max(0.0, min(float(fail_ratio), 1.0))
        normalized["duration_seconds"] = max(0.0, float(normalized["duration_seconds"]))
        normalized["retry_count"] = max(0.0, float(normalized["retry_count"]))
        out_rows.append(normalized)
    return _to_dataframe(out_rows)


def to_feature_matrix(df: Any, feature_cols: list[str]):
    rows = _iter_rows(df)
    matrix: list[list[float]] = []
    for row in rows:
        matrix.append([float(row.get(col, 0.0) or 0.0) for col in feature_cols])
    if np is None:
        return matrix
    if not matrix:
        return np.zeros((0, len(feature_cols)), dtype=np.float64)
    return np.array(matrix, dtype=np.float64)


def normalize_matrix(X: Any):
    if np is None:
        cols = len(X[0]) if X else 0
        mean = [0.0] * cols
        std = [1.0] * cols
        return X, mean, std
    if X.size == 0:
        cols = X.shape[1] if X.ndim == 2 else 0
        return X, np.zeros(cols), np.ones(cols)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std <= 1e-8, 1.0, std)
    return (X - mean) / std, mean, std


def apply_normalization(X: Any, mean: Any, std: Any):
    if np is None:
        return X
    if X.size == 0:
        return X
    safe_std = np.where(std <= 1e-8, 1.0, std)
    return (X - mean) / safe_std


def train_inference_split(
    df: Any,
    *,
    train_ratio: float = 0.8,
) -> tuple[Any, Any]:
    rows = _iter_rows(df)
    if not rows:
        return _to_dataframe([]), _to_dataframe([])

    ratio = max(0.1, min(0.95, float(train_ratio)))
    split_idx = int(len(rows) * ratio)
    split_idx = min(max(split_idx, 1), len(rows))
    return _to_dataframe(rows[:split_idx]), _to_dataframe(rows[split_idx:])
