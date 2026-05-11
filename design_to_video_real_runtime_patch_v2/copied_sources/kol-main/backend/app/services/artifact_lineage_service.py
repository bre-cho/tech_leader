from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class ArtifactLineageRecord:
    id: str = field(default_factory=lambda: str(uuid4()))
    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    parent_artifact_id: str | None = None
    previous_final_checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FileArtifactRecord:
    id: str = field(default_factory=lambda: str(uuid4()))
    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    artifact_type: str | None = None
    path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def record_final_render_artifact(
    db: Any,
    *,
    job: Any,
    artifact: Any,
    lineage_kind: str,
    rerender_reason: str | None = None,
    affected_scene_indexes: list[int] | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> ArtifactLineageRecord:
    del db, commit
    artifact_checksum = getattr(artifact, "sha256", None)
    payload = {
        "lineage_kind": lineage_kind,
        "rerender_reason": rerender_reason,
        "affected_scene_indexes": affected_scene_indexes or [],
        **(metadata or {}),
    }
    return ArtifactLineageRecord(
        parent_artifact_id=getattr(job, "id", None),
        previous_final_checksum=artifact_checksum,
        metadata=payload,
    )


def record_file_artifact(
    db: Any,
    *,
    artifact_type: str,
    path: str,
    project_id: Any,
    render_job_id: Any,
    scene_task_id: Any,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> FileArtifactRecord:
    del db, project_id, render_job_id, scene_task_id, commit
    return FileArtifactRecord(
        artifact_type=artifact_type,
        path=path,
        metadata=metadata or {},
    )
