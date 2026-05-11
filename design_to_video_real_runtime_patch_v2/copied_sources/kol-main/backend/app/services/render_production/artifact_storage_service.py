from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import ArtifactContract, ensure_file, infer_mime, new_artifact_id, now_ts, sha256_file, write_json


class LocalArtifactStorageService:
    """Production-safe local artifact storage.

    Swap this class for S3/MinIO later without changing the orchestrator contract.
    """

    def __init__(self, base_dir: str | Path | None = None, public_base_url: str | None = None):
        self.base_dir = Path(base_dir or os.getenv("RENDER_ARTIFACT_DIR", "./storage/render_artifacts"))
        self.public_base_url = (public_base_url or os.getenv("RENDER_PUBLIC_BASE_URL", "/artifacts")).rstrip("/")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def put_file(
        self,
        *,
        source_path: str | Path,
        artifact_type: str,
        source_job_id: str,
        source_scene_id: Optional[str] = None,
        parent_artifact_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
    ) -> ArtifactContract:
        source = ensure_file(source_path, artifact_type)
        artifact_id = new_artifact_id(artifact_type)
        ext = source.suffix or ".bin"
        safe_filename = filename or f"{artifact_id}{ext}"
        dest_dir = self.base_dir / source_job_id / artifact_type
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / safe_filename
        shutil.copy2(source, dest)
        contract = ArtifactContract(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            mime_type=infer_mime(dest),
            path=str(dest),
            url=f"{self.public_base_url}/{source_job_id}/{artifact_type}/{dest.name}",
            size_bytes=dest.stat().st_size,
            checksum_sha256=sha256_file(dest),
            created_at=now_ts(),
            source_job_id=source_job_id,
            source_scene_id=source_scene_id,
            parent_artifact_ids=parent_artifact_ids or [],
            metadata=metadata or {},
        )
        write_json(dest.with_suffix(dest.suffix + ".contract.json"), contract.to_dict())
        return contract
