from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ArtifactRecord(BaseModel):
    """Full lineage-annotated artifact produced by any runtime or workforce workflow."""

    artifact_id: str
    source_task_id: str
    agent_id: str
    input_hash: str = Field(..., description="sha256 of the serialized input payload")
    runtime_version: str = Field(default="1.0.0")
    parent_artifact_id: Optional[str] = None
    checksum: str = Field(..., description="sha256 of the artifact payload/prompt")
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None).isoformat())
    status: Literal["pending", "ready_to_call", "failed", "promoted"] = "ready_to_call"
    replayable: bool = True
