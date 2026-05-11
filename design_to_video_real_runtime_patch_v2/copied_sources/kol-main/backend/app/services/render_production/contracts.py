from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import mimetypes
import time
import uuid


class RenderProductionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ArtifactContract:
    artifact_id: str
    artifact_type: str
    mime_type: str
    path: str
    url: str
    size_bytes: int
    checksum_sha256: str
    created_at: float
    source_job_id: str
    source_scene_id: Optional[str] = None
    parent_artifact_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinalVideoContract:
    job_id: str
    status: str
    final_video: ArtifactContract
    thumbnail: Optional[ArtifactContract]
    scene_artifacts: List[ArtifactContract]
    audio_artifact: Optional[ArtifactContract]
    subtitle_artifact: Optional[ArtifactContract]
    quality_gate: Dict[str, Any]
    timeline: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "final_video": self.final_video.to_dict(),
            "thumbnail": self.thumbnail.to_dict() if self.thumbnail else None,
            "scene_artifacts": [a.to_dict() for a in self.scene_artifacts],
            "audio_artifact": self.audio_artifact.to_dict() if self.audio_artifact else None,
            "subtitle_artifact": self.subtitle_artifact.to_dict() if self.subtitle_artifact else None,
            "quality_gate": self.quality_gate,
            "timeline": self.timeline,
        }


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_file(path: str | Path, label: str = "artifact") -> Path:
    p = Path(path)
    if not p.exists():
        raise RenderProductionError(f"{label} does not exist: {p}")
    if not p.is_file():
        raise RenderProductionError(f"{label} is not a file: {p}")
    if p.stat().st_size <= 0:
        raise RenderProductionError(f"{label} is empty: {p}")
    return p


def infer_mime(path: str | Path) -> str:
    guess, _ = mimetypes.guess_type(str(path))
    return guess or "application/octet-stream"


def new_artifact_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def write_json(path: str | Path, payload: Dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def now_ts() -> float:
    return time.time()
