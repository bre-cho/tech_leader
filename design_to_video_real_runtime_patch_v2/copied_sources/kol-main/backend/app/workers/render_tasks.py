from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from app.core.async_utils import run_async
from app.core.database import SessionLocal
from app.models.provider_webhook_event import ProviderWebhookEvent
from app.services.artifact_lineage_service import record_final_render_artifact
from app.services.auto_media_qa_hook import run_media_qa_for_render_artifact
from app.services.render_artifact_service import RenderArtifactError, assemble_render_job_artifacts
from app.services.provider_audit_service import estimated_submit_cost, record_provider_audit
from app.services.render_dispatch_service import (
    dispatch_scene_task,
    get_dispatch_runtime_override,
)
from app.services.render_poll_service import poll_scene_task
from app.services.render_repository import (
    attach_final_job_storage,
    finalize_render_job,
    get_render_job_by_id,
    get_scene_task_by_id,
    list_queued_scene_tasks,
    list_successful_scene_tasks,
    mark_job_status,
    mark_scene_failed,
    mark_scene_failed_from_provider,
    mark_scene_processing,
    mark_scene_processing_from_provider,
    mark_scene_submitted,
    mark_scene_succeeded,
    mark_scene_succeeded_from_provider,
    mark_webhook_event_processed,
    should_enqueue_postprocess,
    stage_render_job_for_identity_review,
)
from app.workers.celery_app import celery_app, dispatch_to_dlq

logger = logging.getLogger(__name__)

#: Maximum number of poll cycles for a single scene task before the task is
#: considered timed-out and marked as failed.  Each cycle is separated by
#: ``poll_countdown_seconds`` (default 30 s), so the default of 120 allows
#: up to 60 minutes of processing time per scene.  Override via the
#: ``RENDER_POLL_MAX_ATTEMPTS`` environment variable.
_DEFAULT_POLL_MAX_ATTEMPTS: int = 120


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _task_countdown(retries: int, *, base_seconds: int = 30, max_seconds: int = 300) -> int:
    """Return exponential backoff delay in seconds for Celery task retries.

    ``retries`` is the current retry count (0-indexed), so the first retry
    yields ``base_seconds``. The returned delay grows as ``base * 2**retries``
    and is capped at ``max_seconds``.
    """
    retries = max(0, int(retries))
    base = max(1, int(base_seconds))
    ceiling = max(base, int(max_seconds))
    return min(base * (2 ** retries), ceiling)


def _schedule_dispatch(job_id: str, countdown: int = 0) -> None:
    render_dispatch_task.apply_async(args=[job_id], countdown=max(0, int(countdown)))


def _schedule_poll(job_id: str, scene_task_id: str, countdown: int = 0, poll_attempt: int = 0) -> None:
    render_poll_task.apply_async(args=[job_id, scene_task_id, poll_attempt], countdown=max(0, int(countdown)))


def _schedule_postprocess(job_id: str, countdown: int = 0) -> None:
    render_postprocess_task.apply_async(args=[job_id], countdown=max(0, int(countdown)))


def _load_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, dict) else {}
    except json.JSONDecodeError as exc:
        logger.error(
            "render_tasks: JSON decode error; returning empty payload. "
            "Inspect request_payload_json for corruption. error=%s",
            exc,
        )
        return {}


@celery_app.task(
    name="app.workers.render_tasks.render_dispatch_task",
    bind=True,
    acks_late=True,
    max_retries=3,
    default_retry_delay=30,
)
def render_dispatch_task(self, job_id: str) -> dict[str, Any]:
    with SessionLocal() as db:
        try:
            job = get_render_job_by_id(db, job_id, with_scenes=True)
            if job is None:
                return {"ok": False, "reason": "job_not_found", "job_id": job_id}

            if job.status in {"completed", "failed", "canceled"}:
                return {"ok": True, "reason": "job_terminal", "job_id": job_id, "status": job.status}

            runtime = get_dispatch_runtime_override()
            if not runtime.get("enabled", True):
                return {"ok": True, "reason": "dispatch_disabled", "job_id": job_id}

            dispatch_limit = max(1, int(runtime.get("dispatch_batch_limit", 1)))
            poll_countdown = max(1, int(runtime.get("poll_countdown_seconds", 30)))

            if job.status == "queued":
                mark_job_status(db, job, "dispatching", source="dispatch", reason="dispatch_started")
                job = get_render_job_by_id(db, job_id, with_scenes=True) or job

            queued_scenes = list_queued_scene_tasks(db, job_id)[:dispatch_limit]
            dispatched = 0

            for scene in queued_scenes:
                result = run_async(dispatch_scene_task(scene.provider, scene.request_payload_json))
                request_payload = _load_json(scene.request_payload_json)
                record_provider_audit(
                    db,
                    provider=result.provider or scene.provider,
                    operation="submit",
                    status="accepted" if result.accepted else "failed",
                    job_id=job_id,
                    scene_task_id=scene.id,
                    scene_index=scene.scene_index,
                    idempotency_key=result.idempotency_key or request_payload.get("idempotency_key"),
                    provider_model=result.provider_model,
                    provider_request_id=result.provider_request_id,
                    provider_task_id=result.provider_task_id,
                    provider_operation_name=result.provider_operation_name,
                    provider_status_raw=result.provider_status_raw,
                    accepted=result.accepted,
                    latency_ms=result.latency_ms,
                    retry_after_seconds=result.retry_after_seconds,
                    failure_code=None if result.accepted else "DISPATCH_SUBMIT_FAILED",
                    failure_category=None if result.accepted else "dispatch",
                    error_message=result.error_message,
                    estimated_cost_usd=estimated_submit_cost(result.provider or scene.provider) if result.accepted else 0.0,
                    request_payload=request_payload,
                    response_payload=result.raw_response,
                )

                if result.accepted:
                    marked = mark_scene_submitted(
                        db,
                        scene,
                        provider_task_id=result.provider_task_id,
                        provider_operation_name=result.provider_operation_name,
                        raw_response=result.raw_response,
                        provider_request_id=result.provider_request_id,
                        provider_status_raw=result.provider_status_raw,
                        provider_model=result.provider_model,
                        provider_callback_url=result.callback_url_used,
                        effective_provider=result.provider,
                        source="dispatch",
                    )
                    if marked:
                        dispatched += 1
                        _schedule_poll(job_id, scene.id, poll_countdown)
                else:
                    mark_scene_failed(
                        db,
                        job,
                        scene,
                        message=result.error_message or "provider submit failed",
                        provider_status_raw=result.provider_status_raw,
                        failure_code="DISPATCH_SUBMIT_FAILED",
                        failure_category="dispatch",
                        raw_response=result.raw_response,
                    )

            remaining = list_queued_scene_tasks(db, job_id)
            if dispatched > 0 and job.status == "dispatching":
                mark_job_status(db, job, "polling", source="dispatch", reason="dispatch_submitted")
                job = get_render_job_by_id(db, job_id, with_scenes=True) or job
            if remaining:
                _schedule_dispatch(job_id, countdown=3)

            refreshed = get_render_job_by_id(db, job_id, with_scenes=True)
            if refreshed and should_enqueue_postprocess(refreshed):
                _schedule_postprocess(job_id, countdown=1)

            return {
                "ok": True,
                "job_id": job_id,
                "dispatched": dispatched,
                "remaining_queued": len(remaining),
            }
        except Exception as exc:
            if self.request.retries >= self.max_retries:
                dispatch_to_dlq(self.name, [job_id], {}, str(exc))
            logger.warning("render_dispatch_task failed (attempt %s/%s): %s", self.request.retries + 1, self.max_retries + 1, exc)
            # Exponential backoff capped at 300s: 30s → 60s → 120s → 300s
            retry_countdown = _task_countdown(self.request.retries, base_seconds=30, max_seconds=300)
            raise self.retry(exc=exc, countdown=retry_countdown)


@celery_app.task(
    name="app.workers.render_tasks.render_poll_task",
    bind=True,
    acks_late=True,
    max_retries=3,
    default_retry_delay=30,
)
def render_poll_task(self, job_id: str, scene_task_id: str, poll_attempt: int = 0) -> dict[str, Any]:
    """Poll the provider for a single scene task's completion status.

    Args:
        job_id: The :class:`~app.models.render_job.RenderJob` primary key.
        scene_task_id: The :class:`~app.models.render_scene_task.RenderSceneTask` primary key.
        poll_attempt: Current polling cycle count (0-indexed).  Incremented on
            every ``processing`` response and passed to the next scheduled
            invocation.  When it reaches ``RENDER_POLL_MAX_ATTEMPTS`` the
            scene is marked failed with ``POLL_TIMEOUT``.
    """
    with SessionLocal() as db:
        try:
            job = get_render_job_by_id(db, job_id, with_scenes=True)
            scene = get_scene_task_by_id(db, scene_task_id)
            if job is None or scene is None:
                return {"ok": False, "reason": "job_or_scene_missing", "job_id": job_id, "scene_task_id": scene_task_id}

            if scene.status in {"succeeded", "failed", "canceled"}:
                if should_enqueue_postprocess(job):
                    _schedule_postprocess(job_id, countdown=1)
                return {"ok": True, "reason": "scene_terminal", "scene_status": scene.status}

            result = run_async(
                poll_scene_task(
                    provider=scene.provider,
                    provider_task_id=scene.provider_task_id,
                    provider_operation_name=scene.provider_operation_name,
                )
            )

            record_provider_audit(
                db,
                provider=result.provider or scene.provider,
                operation="query",
                status=result.state,
                job_id=job_id,
                scene_task_id=scene.id,
                scene_index=scene.scene_index,
                provider_model=scene.provider_model,
                provider_request_id=scene.provider_request_id,
                provider_task_id=scene.provider_task_id,
                provider_operation_name=scene.provider_operation_name,
                provider_status_raw=result.provider_status_raw,
                latency_ms=result.latency_ms,
                retry_after_seconds=result.retry_after_seconds,
                failure_code=result.failure_code,
                failure_category=result.failure_category,
                error_message=result.error_message,
                response_payload=result.raw_response,
            )

            if result.state == "processing":
                mark_scene_processing(
                    db,
                    scene,
                    raw_response=result.raw_response,
                    provider_status_raw=result.provider_status_raw,
                    output_metadata=result.metadata,
                )
                poll_countdown = max(1, int(get_dispatch_runtime_override().get("poll_countdown_seconds", 30)))
                next_attempt = poll_attempt + 1
                max_polls = int(os.getenv("RENDER_POLL_MAX_ATTEMPTS", str(_DEFAULT_POLL_MAX_ATTEMPTS)))
                if next_attempt >= max_polls:
                    logger.error(
                        "Poll timeout for scene %s after %d attempts; marking failed.",
                        scene_task_id,
                        next_attempt,
                    )
                    refreshed_job = get_render_job_by_id(db, job_id, with_scenes=True) or job
                    mark_scene_failed(
                        db,
                        refreshed_job,
                        scene,
                        message=f"Provider did not complete after {next_attempt} poll attempts",
                        provider_status_raw=result.provider_status_raw,
                        failure_code="POLL_TIMEOUT",
                        failure_category="provider_poll",
                        raw_response=result.raw_response,
                    )
                    refreshed = get_render_job_by_id(db, job_id, with_scenes=True)
                    if refreshed and should_enqueue_postprocess(refreshed):
                        _schedule_postprocess(job_id, countdown=1)
                    return {"ok": False, "reason": "poll_timeout", "job_id": job_id, "scene_task_id": scene_task_id, "attempts": next_attempt}
                _schedule_poll(job_id, scene_task_id, countdown=poll_countdown, poll_attempt=next_attempt)
                return {"ok": True, "state": "processing", "scene_task_id": scene_task_id, "poll_attempt": next_attempt}

            if result.state == "succeeded":
                mark_scene_succeeded(
                    db,
                    job,
                    scene,
                    output_video_url=result.output_video_url,
                    output_thumbnail_url=result.output_thumbnail_url,
                    local_video_path=None,
                    raw_response=result.raw_response,
                    provider_status_raw=result.provider_status_raw,
                    output_metadata=result.metadata,
                )
            else:
                mark_scene_failed(
                    db,
                    job,
                    scene,
                    message=result.error_message or "provider poll failed",
                    provider_status_raw=result.provider_status_raw,
                    failure_code=result.failure_code or "POLL_FAILED",
                    failure_category=result.failure_category or "provider_poll",
                    raw_response=result.raw_response,
                )

            refreshed = get_render_job_by_id(db, job_id, with_scenes=True)
            if refreshed and should_enqueue_postprocess(refreshed):
                _schedule_postprocess(job_id, countdown=1)

            return {
                "ok": True,
                "state": result.state,
                "job_id": job_id,
                "scene_task_id": scene_task_id,
            }
        except Exception as exc:
            if self.request.retries >= self.max_retries:
                dispatch_to_dlq(self.name, [job_id, scene_task_id, poll_attempt], {}, str(exc))
            logger.warning("render_poll_task failed (attempt %s/%s): %s", self.request.retries + 1, self.max_retries + 1, exc)
            # Exponential backoff capped at 300s: 30s → 60s → 120s → 300s
            retry_countdown = _task_countdown(self.request.retries, base_seconds=30, max_seconds=300)
            raise self.retry(exc=exc, countdown=retry_countdown)


@celery_app.task(
    name="app.workers.render_tasks.render_postprocess_task",
    bind=True,
    acks_late=True,
    max_retries=3,
    default_retry_delay=60,
)
def render_postprocess_task(self, job_id: str) -> dict[str, Any]:
    with SessionLocal() as db:
        try:
            job = get_render_job_by_id(db, job_id, with_scenes=True)
            if job is None:
                return {"ok": False, "reason": "job_not_found", "job_id": job_id}

            if job.status in {"completed", "failed", "canceled"}:
                return {"ok": True, "reason": "job_terminal", "status": job.status}

            if not should_enqueue_postprocess(job):
                return {"ok": True, "reason": "postprocess_not_ready", "job_id": job_id}

            successful = list_successful_scene_tasks(db, job_id)
            if not successful:
                mark_job_status(db, job, "failed", source="postprocess", reason="no_successful_scene", error_message="No successful scene to compose final video")
                return {"ok": False, "reason": "no_successful_scene", "job_id": job_id}

            if len(successful) < int(job.planned_scene_count or 0):
                mark_job_status(
                    db,
                    job,
                    "failed",
                    source="postprocess",
                    reason="not_all_scenes_succeeded",
                    error_message="Final assembly requires every planned scene to succeed",
                    metadata={"planned_scene_count": job.planned_scene_count, "successful_scene_count": len(successful)},
                )
                return {"ok": False, "reason": "not_all_scenes_succeeded", "job_id": job_id}

            mark_job_status(db, job, "merging", source="postprocess", reason="ffmpeg_merge_started")
            job = get_render_job_by_id(db, job_id, with_scenes=True) or job

            try:
                artifact = run_async(assemble_render_job_artifacts(job, successful))
                lineage = record_final_render_artifact(
                    db,
                    job=job,
                    artifact=artifact,
                    lineage_kind="postprocess_final_assembly",
                    metadata={"source": "render_postprocess_task"},
                    commit=False,
                )
            except RenderArtifactError as exc:
                logger.exception("render artifact assembly failed for job %s", job_id)
                mark_job_status(db, job, "failed", source="postprocess", reason="artifact_assembly_failed", error_message=str(exc))
                return {"ok": False, "reason": "artifact_assembly_failed", "job_id": job_id, "error": str(exc)}

            attach_final_job_storage(db, job, bucket=artifact.storage_bucket, key=artifact.storage_key, signed_url=artifact.final_video_url)

            staged = stage_render_job_for_identity_review(
                db,
                job,
                final_video_url=artifact.final_video_url,
                final_video_path=artifact.final_video_path,
                final_timeline=artifact.timeline,
                source="postprocess",
            )

            if not staged:
                mark_job_status(db, job, "failed", source="postprocess", reason="stage_identity_review_failed", error_message="Failed to transition render job to identity_review")
                return {"ok": False, "reason": "stage_identity_review_failed", "job_id": job_id}

            try:
                run_media_qa_for_render_artifact(
                    db,
                    project_id=job.project_id,
                    render_job_id=job.id,
                    final_video_url=artifact.final_video_url,
                    artifact_id=lineage.artifact_id,
                    artifact_checksum=artifact.sha256,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("auto media QA hook failed for job %s: %s", job_id, exc)

            render_identity_review_task.apply_async(args=[job_id], countdown=1)
            return {
                "ok": True,
                "job_id": job_id,
                "status": "identity_review",
                "final_video_url": artifact.final_video_url,
                "final_video_path": artifact.final_video_path,
                "sha256": artifact.sha256,
                "size_bytes": artifact.size_bytes,
                "lineage_id": lineage.id,
            }
        except Exception as exc:
            if self.request.retries >= self.max_retries:
                dispatch_to_dlq(self.name, [job_id], {}, str(exc))
            logger.warning("render_postprocess_task failed (attempt %s/%s): %s", self.request.retries + 1, self.max_retries + 1, exc)
            # Exponential backoff capped at 300s: 60s → 120s → 300s
            retry_countdown = _task_countdown(self.request.retries, base_seconds=60, max_seconds=300)
            raise self.retry(exc=exc, countdown=retry_countdown)

@celery_app.task(
    name="app.workers.render_tasks.render_identity_review_task",
    bind=True,
    acks_late=True,
    max_retries=2,
    default_retry_delay=30,
)
def render_identity_review_task(self, job_id: str) -> dict[str, Any]:
    """Perform avatar identity gate check and finalize the render job.

    Delegates to
    :func:`~app.workers.render_identity_review_worker.process_render_identity_review`
    which runs the full QA pipeline (identity gate + quality check), then
    finalizes the job to ``completed``, packages SEO metadata, and
    auto-creates a publish job.

    Flow:
    1. Load the job (expected status: ``identity_review``).
    2. Run QA + identity review pipeline.
    3. Return final job status.
    """
    with SessionLocal() as db:
        try:
            job = get_render_job_by_id(db, job_id, with_scenes=False)
            if job is None:
                return {"ok": False, "reason": "job_not_found", "job_id": job_id}

            if job.status not in {"identity_review", "merging", "burning_subtitles"}:
                # Job already transitioned by another path (e.g. previously completed
                # or failed).  Nothing to do.
                return {"ok": True, "reason": "not_in_identity_review", "job_id": job_id, "status": job.status}

            from app.workers.render_identity_review_worker import process_render_identity_review  # noqa: PLC0415
            try:
                run_async(process_render_identity_review(db, job_id))
            except Exception as qa_exc:
                raise RuntimeError(
                    f"render_identity_review_task: identity review pipeline failed for job {job_id}: {qa_exc}"
                ) from qa_exc

            # Re-read status after QA pipeline ran
            updated = get_render_job_by_id(db, job_id, with_scenes=False)
            final_status = updated.status if updated else "unknown"
            logger.info(
                "render_identity_review_task: job=%s final_status=%s",
                job_id,
                final_status,
            )
            return {"ok": True, "job_id": job_id, "status": final_status}
        except Exception as exc:
            if self.request.retries >= self.max_retries:
                dispatch_to_dlq(self.name, [job_id], {}, str(exc))
            logger.warning(
                "render_identity_review_task failed (attempt %s/%s): %s",
                self.request.retries + 1,
                self.max_retries + 1,
                exc,
            )
            # Exponential backoff capped at 120s: 30s → 60s → 120s
            retry_countdown = _task_countdown(self.request.retries, base_seconds=30, max_seconds=120)
            raise self.retry(exc=exc, countdown=retry_countdown)


@celery_app.task(
    name="app.workers.render_tasks.render_callback_process_task",
    bind=True,
    acks_late=True,
    max_retries=3,
    default_retry_delay=30,
)
def render_callback_process_task(self, event_id: str) -> dict[str, Any]:
    with SessionLocal() as db:
        try:
            event = db.query(ProviderWebhookEvent).filter(ProviderWebhookEvent.id == event_id).first()
            if event is None:
                return {"ok": False, "reason": "event_not_found", "event_id": event_id}

            if event.processed:
                return {"ok": True, "reason": "already_processed", "event_id": event_id}

            normalized = _load_json(event.normalized_payload_json)
            scene = None
            if event.scene_task_id:
                scene = get_scene_task_by_id(db, event.scene_task_id)

            if scene is None and event.provider_task_id:
                # Conservative fallback: scene was not resolved at ingest stage.
                from app.services.render_repository import find_scene_by_provider_refs

                scene = find_scene_by_provider_refs(
                    db,
                    provider=event.provider,
                    provider_task_id=event.provider_task_id,
                    provider_operation_name=event.provider_operation_name,
                )

            if scene is not None:
                state = str(normalized.get("state") or "processing")
                provider_status_raw = normalized.get("provider_status_raw")
                metadata = normalized.get("metadata") if isinstance(normalized.get("metadata"), dict) else None

                if state == "processing":
                    mark_scene_processing_from_provider(
                        db,
                        scene,
                        provider_status_raw=provider_status_raw,
                        metadata=metadata,
                        raw_response=normalized,
                    )
                elif state == "succeeded":
                    mark_scene_succeeded_from_provider(
                        db,
                        scene,
                        provider_status_raw=provider_status_raw,
                        output_video_url=normalized.get("output_video_url"),
                        output_thumbnail_url=normalized.get("output_thumbnail_url"),
                        metadata=metadata,
                        raw_response=normalized,
                    )
                elif state in {"failed", "canceled"}:
                    mark_scene_failed_from_provider(
                        db,
                        scene,
                        provider_status_raw=provider_status_raw,
                        error_message=normalized.get("error_message"),
                        failure_code=normalized.get("failure_code"),
                        failure_category=normalized.get("failure_category"),
                        raw_response=normalized,
                    )

                job = get_render_job_by_id(db, scene.job_id, with_scenes=True)
                if job and should_enqueue_postprocess(job):
                    _schedule_postprocess(scene.job_id, countdown=1)

            mark_webhook_event_processed(db, event)
            return {"ok": True, "event_id": event_id, "scene_task_id": scene.id if scene else None}
        except Exception as exc:  # noqa: BLE001
            if self.request.retries >= self.max_retries:
                dispatch_to_dlq(self.name, [event_id], {}, str(exc))
            logger.warning(
                "render_callback_process_task failed (attempt %s/%s): %s",
                self.request.retries + 1,
                self.max_retries + 1,
                exc,
            )
            retry_countdown = _task_countdown(self.request.retries, base_seconds=30, max_seconds=120)
            raise self.retry(exc=exc, countdown=retry_countdown)
