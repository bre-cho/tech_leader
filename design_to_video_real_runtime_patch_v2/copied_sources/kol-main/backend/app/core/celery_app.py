from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)


def dispatch_to_dlq(
    task_id: str,
    error: str | None = None,
    *,
    job_id: str | None = None,
    scene_task_id: str | None = None,
    scene_index: int | None = None,
    provider: str | None = None,
    reason_code: str = "unspecified",
    failure_category: str | None = None,
    retry_count: int = 0,
    payload: dict | None = None,
) -> dict:
    """Persist a failed render task to the dead-letter queue (``render_dead_letter_events``).

    Writes an immutable audit row to the DB so operators can inspect and
    requeue failed tasks from the render dashboard instead of losing them.

    Falls back gracefully when the DB is unavailable so a DLQ write failure
    never silently swallows the original error.

    Parameters
    ----------
    task_id:
        Celery task ID or internal task identifier.
    error:
        Human-readable error message.
    job_id:
        Associated RenderJob ID (optional but strongly recommended).
    scene_task_id:
        Associated RenderSceneTask ID (optional).
    scene_index:
        Scene index within the job (optional).
    provider:
        Provider name that caused the failure (optional).
    reason_code:
        Machine-readable failure code for grouping/alerting (default: "unspecified").
    failure_category:
        Broad failure category, e.g. "quota", "transient", "fatal" (optional).
    retry_count:
        Number of retries already attempted before this DLQ dispatch.
    payload:
        Arbitrary context dict serialised to JSON and stored alongside the event.
    """
    try:
        from app.db.session import SessionLocal  # noqa: PLC0415
        from app.models.render_dead_letter_event import RenderDeadLetterEvent  # noqa: PLC0415

        event = RenderDeadLetterEvent(
            job_id=str(job_id or task_id),
            scene_task_id=str(scene_task_id) if scene_task_id else None,
            scene_index=scene_index,
            provider=str(provider) if provider else None,
            status="open",
            reason_code=reason_code[:128],
            failure_category=str(failure_category)[:64] if failure_category else None,
            error_message=str(error)[:4096] if error else None,
            retry_count=retry_count,
            payload_json=json.dumps(
                {
                    "task_id": task_id,
                    **(payload or {}),
                },
                ensure_ascii=False,
                default=str,
            ),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        with SessionLocal() as db:
            db.add(event)
            db.commit()
            dlq_event_id = event.id
        logger.info(
            "dispatch_to_dlq: task_id=%s job_id=%s reason=%s → dlq_event=%s",
            task_id,
            job_id,
            reason_code,
            dlq_event_id,
        )
        return {"ok": True, "task_id": task_id, "dlq_reason": error or "unspecified", "dlq_event_id": dlq_event_id}
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "dispatch_to_dlq: failed to persist DLQ event for task_id=%s: %s — event lost",
            task_id,
            exc,
        )
        return {"ok": False, "task_id": task_id, "dlq_reason": error or "unspecified", "error": str(exc)}


celery_app = Celery(
    "render_factory",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.render_tasks",
        "app.workers.narration_worker",
        "app.workers.audio_preview_worker",
        "app.workers.music_worker",
        "app.workers.audio_mix_worker",
        "app.workers.video_mux_worker",
        "app.workers.voice_clone_worker",
        "app.workers.rag_index_worker",
        "app.workers.avatar_ranking_worker",
        "app.drama.workers.drama_scene_worker",
        "app.drama.workers.continuity_rebuild_worker",
        "app.drama.workers.drama_arc_worker",
        "app.drama.workers.retrain_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=settings.celery_task_acks_late,
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    worker_send_task_events=True,
    task_send_sent_event=True,
    timezone="UTC",
    enable_utc=True,
    # Route tasks to dedicated queues so separate worker pools can be
    # configured per queue (e.g. higher concurrency for poll, single worker
    # for postprocess, low-priority queue for template work).
    task_routes={
        "render.dispatch": {"queue": "render_dispatch"},
        "render.poll": {"queue": "render_poll"},
        "render.postprocess": {"queue": "render_postprocess"},
        "render.identity_review": {"queue": "render_postprocess"},
        "render.callback_process": {"queue": "render_callback"},
        "rag.rebuild_index": {"queue": "rag"},
        "audio.run_narration": {"queue": "audio"},
        "audio.run_preview": {"queue": "audio"},
        "audio.generate_music": {"queue": "audio"},
        "audio.mix_tracks": {"queue": "audio"},
        "audio.mux_video": {"queue": "audio"},
        "audio.clone_voice_profile": {"queue": "audio"},
        "app.drama.workers.process_scene": {"queue": "drama"},
        "app.drama.workers.rebuild_continuity": {"queue": "drama"},
        "app.drama.workers.recompute_arcs": {"queue": "drama"},
        "drama.retrain_models": {"queue": "drama"},
    },
    # Default queue for any task not explicitly routed above.
    task_default_queue="celery",
)

celery_app.conf.beat_schedule = {
    "rag-rebuild-index": {
        "task": "rag.rebuild_index",
        "schedule": float(os.environ.get("RAG_INDEX_REBUILD_INTERVAL_SECONDS", "3600")),
    },
    # Drama ML model retraining — runs weekly by default.
    # Interval is configurable via DRAMA_RETRAIN_INTERVAL_SECONDS (default: 7 days).
    # Set to 0 to disable.  Requires DRAMA_RETRAIN_ENABLED=true and a valid
    # DATABASE_URL pointing to a DB with the drama_scene_*_labels tables.
    "drama-retrain-models": {
        "task": "drama.retrain_models",
        "schedule": float(os.environ.get("DRAMA_RETRAIN_INTERVAL_SECONDS", str(7 * 24 * 3600))),
    },
}


def assert_required_tasks_registered() -> None:
    """Smoke-check that required Celery tasks are registered in the current worker process.

    Call this after ``celery_app`` is fully configured (e.g. at the top of a
    worker entrypoint or in a ``worker_ready`` signal handler) to surface missing
    task registrations at startup rather than silently at scheduling time.

    Raises ``RuntimeError`` if any required task is absent.
    """
    required_tasks = [
        "rag.rebuild_index",
        "drama.retrain_models",
        "audio.run_narration",
        "audio.run_preview",
        "audio.generate_music",
        "audio.mix_tracks",
        "audio.mux_video",
        "audio.clone_voice_profile",
    ]
    registered = set(celery_app.tasks.keys())
    missing = [t for t in required_tasks if t not in registered]
    if missing:
        raise RuntimeError(
            "Celery worker boot: required tasks are not registered — "
            + ", ".join(missing)
            + ". Ensure all worker modules are importable and included in celery_app."
        )
    logger.info("assert_required_tasks_registered: all %d required tasks present", len(required_tasks))
