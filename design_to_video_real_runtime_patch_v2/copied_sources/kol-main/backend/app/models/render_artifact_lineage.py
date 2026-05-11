from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RenderArtifactLineage(Base):
    """Durable parent/child lineage for final, rerendered, scene, audio and subtitle artifacts."""

    __tablename__ = "render_artifact_lineage"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    artifact_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lineage_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="created", index=True)

    project_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    render_job_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    scene_task_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    factory_run_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    parent_artifact_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    parent_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    previous_final_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    storage_bucket: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    local_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    rerender_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    affected_scene_indexes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class FactoryStageCheckpoint(Base):
    """Idempotency cursor for async Factory stage resume."""

    __tablename__ = "factory_stage_checkpoints"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    stage_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checkpoint_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    input_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    output_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    output_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resume_cursor_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
