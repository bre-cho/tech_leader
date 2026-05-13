from __future__ import annotations

import hashlib
import json
from pathlib import Path
from app.core.contracts import ArtifactContract


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_artifact_contract(result, run_id: str, workflow_id: str, replay_payload: dict):
    replay_hash = sha256_text(json.dumps(replay_payload, sort_keys=True))
    path_or_url = result.get("path") or result.get("url") or ""
    checksum = result.get("checksum") or sha256_text(path_or_url + replay_hash)
    return ArtifactContract(
        artifact_id=f"art_{checksum[:16]}",
        artifact_type="commercial_visual",
        path_or_url=path_or_url,
        mime_type=result.get("mime_type", "application/octet-stream"),
        checksum_sha256=checksum,
        created_by=result.get("provider", "unknown"),
        source_workflow_id=workflow_id,
        replay_payload_hash=replay_hash,
    )
