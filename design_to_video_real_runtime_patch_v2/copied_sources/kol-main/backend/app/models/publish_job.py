from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    # Repository-wide convention: store UTC as naive datetime in DB rows.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_plan_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    publish_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="SIMULATED", index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued", index=True)

    payload: Mapped[Any] = mapped_column(JSON, nullable=False, default=dict)
    request_payload: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    provider_metadata: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    provider_response: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    external_ids: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    error_log: Mapped[Any | None] = mapped_column(JSON, nullable=True)

    provider_publish_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=_now, onupdate=_now, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, index=True)
