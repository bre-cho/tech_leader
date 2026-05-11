"""drama.workers.retrain_worker — Periodic drama ML model retraining task.

Triggered by the Celery beat schedule ``drama-retrain-models`` (default: weekly).
Runs all four drama model trainers in sequence using real data from the DB label
tables when available, or synthetic data as a fallback.

Controlled by:
    DRAMA_RETRAIN_ENABLED    — must be "true" to run (default: false, to opt-in).
    DRAMA_RETRAIN_ARTIFACT_ROOT — artifact root directory (default: /artifacts/models/drama).
    DRAMA_RETRAIN_MIN_SAMPLES  — min labelled rows per model (default: 200).
    DRAMA_RETRAIN_SYNTHETIC_FALLBACK — allow synthetic fallback (default: false).
    DRAMA_RETRAIN_PARALLEL   — run trainers in parallel (default: false).
"""
from __future__ import annotations

import logging
import os

from celery import shared_task

_logger = logging.getLogger(__name__)


@shared_task(
    name="drama.retrain_models",
    bind=True,
    max_retries=0,  # non-retryable: training is idempotent, next beat cycle will retry
    time_limit=int(os.environ.get("DRAMA_RETRAIN_TIME_LIMIT", str(3 * 3600))),
    soft_time_limit=int(os.environ.get("DRAMA_RETRAIN_SOFT_TIME_LIMIT", str(2 * 3600 + 50 * 60))),
)
def retrain_drama_models(self) -> dict:
    """Train (or retrain) all four drama ML models.

    Reads labelled training data from ``drama_scene_*_labels`` tables when
    available.  Falls back to synthetic data when fewer than
    ``DRAMA_RETRAIN_MIN_SAMPLES`` rows are found.

    After training, updates environment variables in the running process so
    the next inference call uses the new artifacts.  A worker restart is still
    required for the env changes to propagate to other workers.

    Returns a dict with per-model training metrics (or error info).
    """
    enabled = os.getenv("DRAMA_RETRAIN_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        _logger.info("drama.retrain_models: DRAMA_RETRAIN_ENABLED is not true — skipping.")
        return {"skipped": True, "reason": "DRAMA_RETRAIN_ENABLED is not set to true"}

    artifact_root = os.getenv("DRAMA_RETRAIN_ARTIFACT_ROOT", "/artifacts/models/drama")
    min_samples = int(os.getenv("DRAMA_RETRAIN_MIN_SAMPLES", "200"))
    synthetic_fallback = os.getenv("DRAMA_RETRAIN_SYNTHETIC_FALLBACK", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }
    parallel = os.getenv("DRAMA_RETRAIN_PARALLEL", "false").strip().lower() in {"1", "true", "yes", "on"}
    db_url = os.getenv("DATABASE_URL", "") or None

    _logger.info(
        "drama.retrain_models: starting — artifact_root=%s min_samples=%d synthetic_fallback=%s parallel=%s",
        artifact_root,
        min_samples,
        synthetic_fallback,
        parallel,
    )

    try:
        from app.ml.training.drama_train_all import train_all  # noqa: PLC0415

        results = train_all(
            artifact_root=artifact_root,
            db_url=db_url,
            synthetic_fallback=synthetic_fallback,
            parallel=parallel,
        )
    except Exception as exc:  # noqa: BLE001
        _logger.error("drama.retrain_models: train_all failed: %s", exc)
        return {"error": str(exc)}

    # Update environment variables so the next warm-start inference call in this
    # worker process picks up the new artifacts.  Other workers require a restart.
    env_map = {
        "tension": "DRAMA_TENSION_MODEL_PATH",
        "intent": "DRAMA_INTENT_MODEL_PATH",
        "subtext": "DRAMA_SUBTEXT_MODEL_PATH",
        "memory_recall": "DRAMA_MEMORY_RECALL_MODEL_PATH",
    }
    for name, metrics in results.items():
        if "error" not in metrics:
            artifact_path = metrics.get("artifact_path", "")
            if artifact_path:
                env_var = env_map.get(name, "")
                if env_var:
                    os.environ[env_var] = artifact_path
                    _logger.info(
                        "drama.retrain_models: %s trained — updated %s=%s",
                        name,
                        env_var,
                        artifact_path,
                    )

    failures = [n for n, m in results.items() if "error" in m]
    if failures:
        _logger.error("drama.retrain_models: %d model(s) failed: %s", len(failures), failures)
    else:
        _logger.info("drama.retrain_models: all models retrained successfully.")

    return results
