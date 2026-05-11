from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.provider_request_audit import ProviderRequestAudit


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _dumps(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return json.dumps({"unserializable": str(value)}, ensure_ascii=False)


def estimated_submit_cost(provider: str) -> float:
    if provider.lower() == "veo":
        return float(settings.veo_estimated_cost_per_submit_usd or 0.0)
    return 0.0


def assert_provider_quota_available(db: Session, *, provider: str) -> None:
    """Fail closed before a real provider submit can burn quota/cost.

    Limits are intentionally simple and DB-backed so they work across workers:
    - per-minute submit rate limit;
    - daily submit quota;
    - optional daily estimated cost limit. Set cost limit to 0 to disable.
    """
    provider = provider.lower()
    now = utcnow()
    one_minute = now - timedelta(minutes=1)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    per_minute = int(settings.provider_submit_rate_limit_per_minute or 0)
    if per_minute > 0:
        recent = (
            db.query(func.count(ProviderRequestAudit.id))
            .filter(
                ProviderRequestAudit.provider == provider,
                ProviderRequestAudit.operation == "submit",
                ProviderRequestAudit.created_at >= one_minute,
                ProviderRequestAudit.status.in_(["accepted", "succeeded", "processing", "submitted"]),
            )
            .scalar()
            or 0
        )
        if recent >= per_minute:
            record_provider_audit(
                db,
                provider=provider,
                operation="quota_block",
                status="blocked",
                failure_code="PROVIDER_RATE_LIMIT_GUARD",
                failure_category="provider_quota",
                error_message=f"submit rate limit exceeded: {recent}/{per_minute} per minute",
            )
            raise RuntimeError(f"provider submit rate limit exceeded for {provider}: {recent}/{per_minute}/min")

    daily_quota = int(settings.provider_daily_submit_quota or 0)
    if daily_quota > 0:
        daily_count = (
            db.query(func.count(ProviderRequestAudit.id))
            .filter(
                ProviderRequestAudit.provider == provider,
                ProviderRequestAudit.operation == "submit",
                ProviderRequestAudit.created_at >= day_start,
                ProviderRequestAudit.status.in_(["accepted", "succeeded", "processing", "submitted"]),
            )
            .scalar()
            or 0
        )
        if daily_count >= daily_quota:
            record_provider_audit(
                db,
                provider=provider,
                operation="quota_block",
                status="blocked",
                failure_code="PROVIDER_DAILY_QUOTA_GUARD",
                failure_category="provider_quota",
                error_message=f"daily submit quota exceeded: {daily_count}/{daily_quota}",
            )
            raise RuntimeError(f"provider daily submit quota exceeded for {provider}: {daily_count}/{daily_quota}")

    cost_limit = float(settings.provider_daily_cost_limit_usd or 0.0)
    if cost_limit > 0:
        spent = (
            db.query(func.coalesce(func.sum(ProviderRequestAudit.estimated_cost_usd), 0.0))
            .filter(
                ProviderRequestAudit.provider == provider,
                ProviderRequestAudit.operation == "submit",
                ProviderRequestAudit.created_at >= day_start,
                ProviderRequestAudit.status.in_(["accepted", "succeeded", "processing", "submitted"]),
            )
            .scalar()
            or 0.0
        )
        next_cost = estimated_submit_cost(provider)
        if float(spent) + next_cost > cost_limit:
            record_provider_audit(
                db,
                provider=provider,
                operation="quota_block",
                status="blocked",
                failure_code="PROVIDER_DAILY_COST_GUARD",
                failure_category="provider_quota",
                error_message=f"daily provider cost limit exceeded: {spent}+{next_cost}>{cost_limit}",
            )
            raise RuntimeError(f"provider daily cost guard blocked {provider}: {spent}+{next_cost}>{cost_limit}")


def record_provider_audit(
    db: Session,
    *,
    provider: str,
    operation: str,
    status: str,
    job_id: str | None = None,
    scene_task_id: str | None = None,
    scene_index: int | None = None,
    idempotency_key: str | None = None,
    provider_model: str | None = None,
    provider_request_id: str | None = None,
    provider_task_id: str | None = None,
    provider_operation_name: str | None = None,
    provider_status_raw: str | None = None,
    accepted: bool | None = None,
    http_status_code: int | None = None,
    latency_ms: int | None = None,
    retry_after_seconds: int | None = None,
    failure_code: str | None = None,
    failure_category: str | None = None,
    error_message: str | None = None,
    estimated_cost_usd: float | None = None,
    request_payload: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
) -> ProviderRequestAudit:
    row = ProviderRequestAudit(
        provider=provider.lower(),
        operation=operation,
        status=status,
        job_id=job_id,
        scene_task_id=scene_task_id,
        scene_index=scene_index,
        idempotency_key=idempotency_key,
        provider_model=provider_model,
        provider_request_id=provider_request_id,
        provider_task_id=provider_task_id,
        provider_operation_name=provider_operation_name,
        provider_status_raw=provider_status_raw,
        accepted=accepted,
        http_status_code=http_status_code,
        latency_ms=latency_ms,
        retry_after_seconds=retry_after_seconds,
        failure_code=failure_code,
        failure_category=failure_category,
        error_message=error_message,
        estimated_cost_usd=estimated_cost_usd,
        request_payload_json=_dumps(request_payload),
        response_payload_json=_dumps(response_payload),
        created_at=utcnow(),
    )
    db.add(row)
    db.commit()
    return row
