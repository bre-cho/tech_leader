from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RenderDeadLetterEvent(Base):
    """Immutable audit row for render tasks that exceeded automated recovery.

    This is intentionally small and append-only. It gives operators a durable
    queue for scenes/jobs that need manual inspection instead of silently
    leaving them as failed rows inside render_scene_tasks.
    """

    __tablename__ = "render_dead_letter_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scene_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    scene_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open", index=True)
    reason_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    failure_category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
