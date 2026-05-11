"""render_identity_review_worker — mandatory QA gate between postprocess and completed.

After postprocess, a job enters ``identity_review`` (not ``completed``).  This
worker:

1. Loads the job and validates it is still in ``identity_review``.
2. Runs ``render_qa_hook.execute_qa_for_job()`` — quality score + avatar identity.
3. On pass  → calls ``finalize_render_job()`` to advance the job to ``completed``,
   then triggers SEO packaging and auto-creates a publish job.
4. On quality fail → job remains in ``quality_remediation`` (set by render_qa_hook).
5. On identity fail → job remains in ``identity_gate_failed`` (set by render_qa_hook).
6. On unexpected QA exception → job transitions to ``identity_review_error`` for
   manual operator review (METRIC ``identity_review_qa_error`` is emitted at ERROR level).

Call ``process_render_identity_review(db, job_id)`` from the Celery task.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.async_utils import run_async
from app.services.render_repository import (
    finalize_render_job,
    get_render_job_by_id,
    mark_job_status,
)
from app.workers.celery_app import celery_app, dispatch_to_dlq
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

_IDENTITY_REVIEW_ALLOWED_STATUS = "identity_review"


async def process_render_identity_review(db: Session, job_id: str) -> None:
    """Run the mandatory identity + quality gate for a job in ``identity_review``."""
    job = get_render_job_by_id(db, job_id, with_scenes=False)
    if not job:
        return

    if job.status != _IDENTITY_REVIEW_ALLOWED_STATUS:
        logger.debug(
            "render_identity_review_worker: job %s is not in identity_review (status=%s); skipping",
            job_id,
            job.status,
        )
        return

    # ------------------------------------------------------------------
    # Run QA pipeline
    # ------------------------------------------------------------------
    qa_result: dict = {}
    try:
        from app.services.avatar.render_qa_hook import execute_qa_for_job

        qa_result = execute_qa_for_job(db, job) or {}
    except Exception as exc:
        logger.error(
            "render_identity_review_worker: QA hook raised unexpected exception for job %s "
            "(error_type=%s): %s — transitioning to identity_review_error for manual operator "
            "review. METRIC identity_review_qa_error job_id=%s error_type=%s",
            job_id,
            type(exc).__name__,
            exc,
            job_id,
            type(exc).__name__,
        )
        # Do NOT auto-pass: transition to a quarantine status so operators can
        # investigate the failed QA infrastructure before the job is published.
        mark_job_status(
            db,
            job,
            "identity_review_error",
            source="identity_review",
            reason=f"qa_hook_exception: {type(exc).__name__}: {exc}",
        )
        return

    new_status = qa_result.get("new_status", "completed")

    # ------------------------------------------------------------------
    # QA passed → finalize the job
    # ------------------------------------------------------------------
    if new_status == "completed":
        # Reload to pick up any status changes made by execute_qa_for_job
        refreshed = get_render_job_by_id(db, job_id, with_scenes=False)
        if not refreshed:
            return

        if refreshed.status == _IDENTITY_REVIEW_ALLOWED_STATUS:
            # execute_qa_for_job did not change the status; finalize now.
            finalized = finalize_render_job(
                db,
                refreshed,
                final_video_url=refreshed.final_video_url or "",
                final_video_path=refreshed.final_video_path or "",
                final_timeline=_load_final_timeline(refreshed),
                source="identity_review",
            )
            if not finalized:
                logger.warning(
                    "render_identity_review_worker: finalize_render_job failed for job %s",
                    job_id,
                )
                return
        else:
            logger.debug(
                "render_identity_review_worker: job %s already advanced to %s by QA hook",
                job_id,
                refreshed.status,
            )

        _trigger_post_completion_hooks(db, job_id)
        return

    # ------------------------------------------------------------------
    # QA decided quality_remediation or identity_gate_failed
    # render_qa_hook already transitioned the job; nothing more to do here.
    # ------------------------------------------------------------------
    logger.info(
        "render_identity_review_worker: job %s routed to %s by QA gate "
        "(quality_passed=%s identity_passed=%s)",
        job_id,
        new_status,
        qa_result.get("quality_passed"),
        qa_result.get("identity_passed"),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_final_timeline(job) -> dict:
    """Safely deserialise the final_timeline stored on the job."""
    import json
    raw = job.final_timeline_json
    if not raw:
        return {}
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _trigger_post_completion_hooks(db: Session, job_id: str) -> None:
    """Fire non-blocking post-completion side-effects after a job is completed."""
    _run_seo_packaging(db, job_id)
    _auto_create_publish_job(db, job_id)


def _run_seo_packaging(db: Session, job_id: str) -> None:
    """Generate SEO package for the completed render (non-blocking)."""
    try:
        from app.services.post_render_seo_orchestrator import PostRenderSEOOrchestrator
        from app.services.render_repository import get_render_job_by_id as _get

        job = _get(db, job_id, with_scenes=False)
        if not job:
            return

        orchestrator = PostRenderSEOOrchestrator()
        seo_package = orchestrator.generate_seo_package(job)
        logger.info(
            "render_identity_review_worker: SEO package generated for job %s: title=%r",
            job_id,
            seo_package.get("title"),
        )
    except Exception as exc:
        logger.warning(
            "render_identity_review_worker: SEO packaging failed for job %s (non-blocking): %s",
            job_id,
            exc,
        )


def _auto_create_publish_job(db: Session, job_id: str) -> None:
    """Auto-create a publish job for the completed render (non-blocking)."""
    try:
        from app.services.render_repository import get_render_job_by_id as _get
        from app.services.publish_scheduler import PublishScheduler, is_publish_simulated
        from app.services.project_workspace_service import load_project

        job = _get(db, job_id, with_scenes=False)
        if not job or not job.final_video_url:
            return

        # Warn operators when the publish pipeline is running in simulated mode:
        # the job will be created in the DB but no real platform upload will occur.
        if is_publish_simulated():
            logger.warning(
                "render_identity_review_worker: PUBLISH_MODE is SIMULATED — "
                "publish job created for render %s will NOT upload to any real platform. "
                "Set PUBLISH_MODE=REAL to enable actual publishing.",
                job_id,
            )

        project = load_project(job.project_id) if job.project_id else None
        platform = "shorts"
        if project:
            platform = project.get("target_platform") or project.get("format") or "shorts"
            if platform not in ("youtube", "tiktok", "instagram", "reels", "shorts"):
                platform = "shorts"

        plan_item = {
            "video_url": job.final_video_url,
            "project_id": job.project_id,
            "render_job_id": job.id,
            "content_goal": (project or {}).get("content_goal"),
            "market_code": (project or {}).get("market_code"),
            "avatar_id": (project or {}).get("avatar_id"),
            "format": platform,
            "day_index": 1,
            "metadata": {
                "render_job_id": job.id,
                "auto_created": True,
            },
        }

        scheduler = PublishScheduler()
        publish_jobs = scheduler.create_publish_jobs(
            db,
            channel_plan_id=None,
            plan_items=[plan_item],
            platform=platform,
        )
        logger.info(
            "render_identity_review_worker: auto-created %d publish job(s) for render job %s",
            len(publish_jobs),
            job_id,
        )
    except Exception as exc:
        logger.warning(
            "render_identity_review_worker: auto-create publish job failed for %s (non-blocking): %s",
            job_id,
            exc,
        )


@celery_app.task(
    name="app.workers.render_identity_review_worker.process_identity_review_task",
    bind=True,
    acks_late=True,
    max_retries=2,
    default_retry_delay=30,
)
def process_identity_review_task(self, job_id: str) -> dict:
    """Celery task entry point for the identity + quality gate pipeline.

    Wraps :func:`process_render_identity_review` so the pipeline can be
    dispatched independently of ``render_tasks.render_identity_review_task``.
    This task is NOT in the Celery beat schedule — it is enqueued by
    ``render_identity_review_task`` after postprocess completes.
    """
    db = SessionLocal()
    try:
        run_async(process_render_identity_review(db, job_id))
        updated = get_render_job_by_id(db, job_id, with_scenes=False)
        return {
            "ok": True,
            "job_id": job_id,
            "status": updated.status if updated else "unknown",
        }
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            dispatch_to_dlq(self.name, [job_id], {}, str(exc))
        logger.warning(
            "process_identity_review_task failed (attempt %s/%s): %s",
            self.request.retries + 1,
            self.max_retries + 1,
            exc,
        )
        raise self.retry(exc=exc)
    finally:
        db.close()
