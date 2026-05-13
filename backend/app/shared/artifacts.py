from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ArtifactContract(BaseModel):
    artifact_id: str
    artifact_type: str
    path: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    source_job_id: str
    created_by: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_artifact(
    *,
    path: str | Path,
    artifact_type: str,
    source_job_id: str,
    created_by: str,
    mime_type: str = "application/octet-stream",
    metadata: Optional[Dict[str, Any]] = None,
) -> ArtifactContract:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"artifact missing: {p}")
    if p.stat().st_size <= 0:
        raise ValueError(f"artifact empty: {p}")
    checksum = sha256_file(p)
    return ArtifactContract(
        artifact_id=f"art_{checksum[:16]}",
        artifact_type=artifact_type,
        path=str(p),
        mime_type=mime_type,
        size_bytes=p.stat().st_size,
        checksum_sha256=checksum,
        source_job_id=source_job_id,
        created_by=created_by,
        metadata=metadata or {},
    )


def write_manifest(path: str | Path, payload: dict[str, Any]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)
