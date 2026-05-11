from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProviderRequestAudit(Base):
    """Immutable-ish audit row for every real provider submit/query/callback decision.

    P4 goal: make provider usage observable and idempotent enough for production:
    - every submit/query has an idempotency key and latency/error category;
    - quota/cost guard can reason from persisted records;
    - retries and dead-letter incidents have a durable provider trace.
    """

    __tablename__ = "provider_request_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # submit/query/callback/quota_block
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    scene_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    scene_index: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    provider_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_operation_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_status_raw: Mapped[str | None] = mapped_column(String(128), nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown", index=True)
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    http_status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retry_after_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    failure_code: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    failure_category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    request_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False, index=True)
