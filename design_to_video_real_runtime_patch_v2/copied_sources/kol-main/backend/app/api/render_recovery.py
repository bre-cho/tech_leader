from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.render_queue import enqueue_render_dispatch, enqueue_render_poll
from app.services.render_recovery_service import (
    RecoveryPolicy,
    list_dead_letter_events,
    manual_retry_failed_job,
    manual_retry_scene,
    scan_and_plan_recovery,
    summarize_actions,
)

router = APIRouter(prefix="/api/v1/render/recovery", tags=["render-recovery"])


class RecoveryScanRequest(BaseModel):
    stuck_after_seconds: int = Field(default=900, ge=30, le=24 * 3600)
    max_retries: int = Field(default=5, ge=0, le=20)
    base_backoff_seconds: int = Field(default=60, ge=1, le=3600)
    max_backoff_seconds: int = Field(default=900, ge=1, le=24 * 3600)
    max_batch_size: int = Field(default=100, ge=1, le=500)
    dry_run: bool = False

    def to_policy(self) -> RecoveryPolicy:
        return RecoveryPolicy(
            stuck_after_seconds=self.stuck_after_seconds,
            max_retries=self.max_retries,
            base_backoff_seconds=self.base_backoff_seconds,
            max_backoff_seconds=self.max_backoff_seconds,
            max_batch_size=self.max_batch_size,
            dry_run=self.dry_run,
        )


class ManualRetryRequest(BaseModel):
    reset_retry_count: bool = False
    enqueue_now: bool = True


@router.post("/scan")
async def run_recovery_scan(payload: RecoveryScanRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Run stuck-scene recovery now.

    Non-dry-run behavior:
    - active stale scenes under retry budget are scheduled for poll retry;
    - scenes over retry budget are dead-lettered and the job is failed for operator review.
    """
    actions = scan_and_plan_recovery(db, payload.to_policy())
    if not payload.dry_run:
        for action in actions:
            if action.action == "retry_poll" and action.scene_task_id:
                countdown = 0
                if action.next_retry_at:
                    # Celery countdown is intentionally conservative here; the worker scan's next_retry_at
                    # remains the source of truth, but manual scan should kick one poll attempt quickly.
                    countdown = 1
                enqueue_render_poll(action.job_id, action.scene_task_id, countdown=countdown)
    return summarize_actions(actions)


@router.post("/jobs/{job_id}/retry")
async def retry_failed_job(job_id: str, payload: ManualRetryRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        actions = manual_retry_failed_job(db, job_id=job_id, reset_retry_count=payload.reset_retry_count)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if payload.enqueue_now:
        enqueue_render_dispatch(job_id, countdown=0)
    return summarize_actions(actions)


@router.post("/jobs/{job_id}/scenes/{scene_task_id}/retry")
async def retry_failed_scene(job_id: str, scene_task_id: str, payload: ManualRetryRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        action = manual_retry_scene(db, job_id=job_id, scene_task_id=scene_task_id, reset_retry_count=payload.reset_retry_count)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if payload.enqueue_now:
        enqueue_render_dispatch(job_id, countdown=0)
    return summarize_actions([action])


@router.get("/dead-letter")
async def get_dead_letter_events(
    status_filter: str = Query(default="open", alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    events = list_dead_letter_events(db, status=status_filter, limit=limit)
    return {
        "total": len(events),
        "items": [
            {
                "id": event.id,
                "job_id": event.job_id,
                "scene_task_id": event.scene_task_id,
                "scene_index": event.scene_index,
                "provider": event.provider,
                "status": event.status,
                "reason_code": event.reason_code,
                "failure_category": event.failure_category,
                "error_message": event.error_message,
                "retry_count": event.retry_count,
                "created_at": event.created_at,
                "resolved_at": event.resolved_at,
            }
            for event in events
        ],
    }
