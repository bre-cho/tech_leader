from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.render_dead_letter_event import RenderDeadLetterEvent
from app.models.render_incident_state import RenderIncidentState
from app.models.render_job import RenderJob
from app.models.render_scene_task import RenderSceneTask
from app.services.render_repository import (
    append_timeline_event,
    get_render_job_by_id,
    mark_job_status,
    requeue_failed_scene,
    should_enqueue_postprocess,
)

ACTIVE_SCENE_STATUSES = {"submitted", "processing"}
FAILED_SCENE_STATUSES = {"failed", "canceled"}
TERMINAL_JOB_STATUSES = {"completed", "failed", "canceled"}
DEFAULT_STUCK_AFTER_SECONDS = 15 * 60
DEFAULT_MAX_RETRIES = 5
DEFAULT_BASE_BACKOFF_SECONDS = 60
DEFAULT_MAX_BACKOFF_SECONDS = 15 * 60


@dataclass(slots=True)
class RecoveryPolicy:
    stuck_after_seconds: int = DEFAULT_STUCK_AFTER_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    base_backoff_seconds: int = DEFAULT_BASE_BACKOFF_SECONDS
    max_backoff_seconds: int = DEFAULT_MAX_BACKOFF_SECONDS
    max_batch_size: int = 100
    dry_run: bool = False


@dataclass(slots=True)
class RecoveryAction:
    action: str
    job_id: str
    scene_task_id: str | None = None
    reason: str | None = None
    retry_count: int | None = None
    next_retry_at: datetime | None = None
    dead_letter_event_id: str | None = None


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _loads(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _dumps(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, default=str)


def compute_backoff_seconds(retry_count: int, policy: RecoveryPolicy) -> int:
    delay = int(policy.base_backoff_seconds) * (2 ** max(int(retry_count or 0), 0))
    return min(delay, int(policy.max_backoff_seconds))


def _scene_last_activity(scene: RenderSceneTask) -> datetime | None:
    candidates = [
        scene.last_callback_at,
        scene.last_polled_at,
        scene.provider_status_observed_at,
        scene.started_at,
        scene.submitted_at,
        scene.updated_at,
        scene.created_at,
    ]
    return max([c for c in candidates if c is not None], default=None)


def list_stuck_scenes(db: Session, policy: RecoveryPolicy) -> list[RenderSceneTask]:
    threshold = utcnow() - timedelta(seconds=policy.stuck_after_seconds)
    return (
        db.query(RenderSceneTask)
        .options(selectinload(RenderSceneTask.job))
        .filter(
            RenderSceneTask.poll_fallback_enabled.is_(True),
            RenderSceneTask.status.in_(list(ACTIVE_SCENE_STATUSES)),
            or_(RenderSceneTask.next_retry_at.is_(None), RenderSceneTask.next_retry_at <= utcnow()),
            or_(
                RenderSceneTask.last_callback_at.is_(None),
                RenderSceneTask.last_callback_at < threshold,
            ),
            or_(
                RenderSceneTask.last_polled_at.is_(None),
                RenderSceneTask.last_polled_at < threshold,
            ),
        )
        .order_by(RenderSceneTask.retry_count.asc(), RenderSceneTask.updated_at.asc())
        .limit(policy.max_batch_size)
        .all()
    )


def create_dead_letter_event(
    db: Session,
    *,
    scene: RenderSceneTask,
    reason_code: str,
    error_message: str,
    payload: dict[str, Any] | None = None,
) -> RenderDeadLetterEvent:
    event = RenderDeadLetterEvent(
        job_id=scene.job_id,
        scene_task_id=scene.id,
        scene_index=scene.scene_index,
        provider=scene.provider,
        status="open",
        reason_code=reason_code,
        failure_category=scene.failure_category or "recovery",
        error_message=error_message,
        retry_count=int(scene.retry_count or 0),
        payload_json=_dumps(payload or {}),
        created_at=utcnow(),
    )
    db.add(event)
    return event


def create_dead_letter_incident(db: Session, *, scene: RenderSceneTask, reason: str, dead_letter_event_id: str | None) -> RenderIncidentState:
    job = scene.job or get_render_job_by_id(db, scene.job_id, with_scenes=False)
    now = utcnow()
    incident_key = f"render-dead-letter:{scene.job_id}:{scene.id}"
    row = db.query(RenderIncidentState).filter(RenderIncidentState.incident_key == incident_key).one_or_none()
    if row:
        row.last_seen_at = now
        row.last_transition_at = now
        row.current_event_id = dead_letter_event_id
        row.current_event_type = "scene_dead_lettered"
        row.status = "open" if row.status == "resolved" else row.status
        row.note = reason
        return row
    row = RenderIncidentState(
        id=str(uuid.uuid4()),
        incident_key=incident_key,
        job_id=scene.job_id,
        project_id=getattr(job, "project_id", "unknown") or "unknown",
        provider=scene.provider or getattr(job, "provider", "unknown") or "unknown",
        incident_family="render_dead_letter",
        current_event_id=dead_letter_event_id,
        current_event_type="scene_dead_lettered",
        current_severity_rank=90,
        first_seen_at=now,
        last_seen_at=now,
        last_transition_at=now,
        status="open",
        note=reason,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    return row

def dead_letter_scene(db: Session, scene: RenderSceneTask, *, reason: str, policy: RecoveryPolicy) -> RecoveryAction:
    if policy.dry_run:
        return RecoveryAction("would_dead_letter", scene.job_id, scene.id, reason, int(scene.retry_count or 0))

    job = scene.job or get_render_job_by_id(db, scene.job_id, with_scenes=True)
    now = utcnow()
    old_status = scene.status
    scene.status = "failed"
    scene.recovery_status = "dead_lettered"
    scene.dead_lettered_at = now
    scene.finished_at = now
    scene.failure_code = scene.failure_code or "RECOVERY_RETRY_EXHAUSTED"
    scene.failure_category = scene.failure_category or "recovery"
    scene.error_message = scene.error_message or reason
    scene.last_stalled_at = now

    if job:
        job.recovery_status = "needs_operator_review"
        job.last_recovery_scan_at = now
        if job.status not in TERMINAL_JOB_STATUSES:
            job.status = "failed"
            job.error_message = f"Render recovery dead-lettered scene {scene.scene_index}: {reason}"
            job.completed_at = now

    event = create_dead_letter_event(
        db,
        scene=scene,
        reason_code="RECOVERY_RETRY_EXHAUSTED",
        error_message=reason,
        payload={
            "old_status": old_status,
            "retry_count": scene.retry_count,
            "last_activity_at": _scene_last_activity(scene),
            "policy": asdict(policy),
        },
    )
    db.flush()
    incident = create_dead_letter_incident(db, scene=scene, reason=reason, dead_letter_event_id=event.id)
    db.flush()
    append_timeline_event(
        db,
        job_id=scene.job_id,
        scene_task_id=scene.id,
        scene_index=scene.scene_index,
        source="recovery",
        event_type="scene_dead_lettered",
        status="failed",
        provider=scene.provider,
        failure_code=scene.failure_code,
        failure_category=scene.failure_category,
        error_message=reason,
        payload={"dead_letter_event_id": event.id, "incident_key": incident.incident_key, "old_status": old_status},
        _flush_only=True,
    )
    db.commit()
    return RecoveryAction("dead_lettered", scene.job_id, scene.id, reason, int(scene.retry_count or 0), dead_letter_event_id=event.id)


def retry_stuck_scene(db: Session, scene: RenderSceneTask, *, policy: RecoveryPolicy) -> RecoveryAction:
    retry_count = int(scene.retry_count or 0)
    reason = f"Scene had no provider progress for {policy.stuck_after_seconds}s"
    if retry_count >= policy.max_retries:
        return dead_letter_scene(db, scene, reason=reason, policy=policy)

    delay = compute_backoff_seconds(retry_count, policy)
    next_retry_at = utcnow() + timedelta(seconds=delay)
    if policy.dry_run:
        return RecoveryAction("would_retry_poll", scene.job_id, scene.id, reason, retry_count + 1, next_retry_at)

    scene.retry_count = retry_count + 1
    scene.recovery_status = "poll_retry_scheduled"
    scene.next_retry_at = next_retry_at
    scene.last_stalled_at = utcnow()
    if scene.job:
        scene.job.recovery_status = "recovering"
        scene.job.last_recovery_scan_at = utcnow()

    append_timeline_event(
        db,
        job_id=scene.job_id,
        scene_task_id=scene.id,
        scene_index=scene.scene_index,
        source="recovery",
        event_type="scene_poll_retry_scheduled",
        status=scene.status,
        provider=scene.provider,
        provider_status_raw=scene.provider_status_raw,
        provider_request_id=scene.provider_request_id,
        provider_task_id=scene.provider_task_id,
        provider_operation_name=scene.provider_operation_name,
        payload={"retry_count": scene.retry_count, "next_retry_at": next_retry_at, "reason": reason},
        _flush_only=True,
    )
    db.commit()
    return RecoveryAction("retry_poll", scene.job_id, scene.id, reason, scene.retry_count, next_retry_at)


def scan_and_plan_recovery(db: Session, policy: RecoveryPolicy | None = None) -> list[RecoveryAction]:
    policy = policy or RecoveryPolicy()
    actions: list[RecoveryAction] = []
    for scene in list_stuck_scenes(db, policy):
        actions.append(retry_stuck_scene(db, scene, policy=policy))
    return actions


def manual_retry_scene(db: Session, *, job_id: str, scene_task_id: str, reset_retry_count: bool = False) -> RecoveryAction:
    job = get_render_job_by_id(db, job_id, with_scenes=True)
    if not job:
        raise ValueError("render job not found")
    scene = next((s for s in job.scenes if s.id == scene_task_id), None)
    if not scene:
        raise ValueError("scene task not found")
    if scene.status not in FAILED_SCENE_STATUSES:
        raise ValueError(f"scene must be failed/canceled before manual retry, got {scene.status}")

    ok = requeue_failed_scene(db, job, scene, source="manual_recovery")
    if not ok:
        raise ValueError("scene could not be requeued")
    db.refresh(scene)
    if reset_retry_count:
        scene.retry_count = 0
    scene.recovery_status = "manual_retry_requested"
    scene.next_retry_at = None
    scene.dead_lettered_at = None
    scene.manual_retry_requested_at = utcnow()
    job.recovery_status = "manual_retry_requested"
    job.status = "queued"
    job.error_message = None
    db.commit()
    return RecoveryAction("manual_scene_requeued", job_id, scene_task_id, "manual retry requested", int(scene.retry_count or 0))


def manual_retry_failed_job(db: Session, *, job_id: str, reset_retry_count: bool = False) -> list[RecoveryAction]:
    job = get_render_job_by_id(db, job_id, with_scenes=True)
    if not job:
        raise ValueError("render job not found")
    actions: list[RecoveryAction] = []
    for scene in job.scenes:
        if scene.status in FAILED_SCENE_STATUSES:
            actions.append(manual_retry_scene(db, job_id=job_id, scene_task_id=scene.id, reset_retry_count=reset_retry_count))
    if not actions:
        raise ValueError("no failed/canceled scenes found for retry")
    return actions


def list_dead_letter_events(db: Session, *, status: str = "open", limit: int = 100) -> list[RenderDeadLetterEvent]:
    return (
        db.query(RenderDeadLetterEvent)
        .filter(RenderDeadLetterEvent.status == status)
        .order_by(RenderDeadLetterEvent.created_at.desc())
        .limit(limit)
        .all()
    )


def summarize_actions(actions: Iterable[RecoveryAction]) -> dict[str, Any]:
    items = list(actions)
    counts: dict[str, int] = {}
    for item in items:
        counts[item.action] = counts.get(item.action, 0) + 1
    return {
        "total": len(items),
        "counts": counts,
        "actions": [
            {
                "action": a.action,
                "job_id": a.job_id,
                "scene_task_id": a.scene_task_id,
                "reason": a.reason,
                "retry_count": a.retry_count,
                "next_retry_at": a.next_retry_at,
                "dead_letter_event_id": a.dead_letter_event_id,
            }
            for a in items
        ],
    }
