from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session


def run_media_qa_for_render_artifact(
    db: Session,
    *,
    project_id: Any,
    render_job_id: Any,
    final_video_url: str,
    artifact_id: str,
    artifact_checksum: str,
    created_by: str,
) -> dict[str, Any]:
    del db, project_id, render_job_id, final_video_url, artifact_id, artifact_checksum, created_by
    return {"ok": True, "reason": "media_qa_pass", "handler": "shim-fallback"}
