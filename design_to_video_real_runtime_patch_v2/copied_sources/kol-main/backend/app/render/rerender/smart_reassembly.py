from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.render_job import RenderJob
from app.models.render_scene_task import RenderSceneTask
from app.services.auto_media_qa_hook import run_media_qa_for_render_artifact
from app.services.artifact_lineage_service import record_final_render_artifact
from app.services.render_artifact_service import assemble_render_job_artifacts


async def smart_reassemble_render_job(db: Session, render_job_id: str, affected_scene_indexes: list[int] | None = None, rerender_reason: str | None = None) -> dict[str, Any]:
    """Run final assembly using the current succeeded scene assets.

    The affected_scene_indexes are recorded in the returned metadata for audit;
    the final assembly still uses every succeeded scene in sequence to guarantee
    a valid complete MP4.
    """
    job = db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
    if job is None:
        raise ValueError(f"RenderJob {render_job_id} not found")
    scenes = (
        db.query(RenderSceneTask)
        .filter(RenderSceneTask.job_id == render_job_id, RenderSceneTask.status == "succeeded")
        .order_by(RenderSceneTask.scene_index.asc())
        .all()
    )
    if len(scenes) < int(job.planned_scene_count or 0):
        raise ValueError("Smart reassembly requires all planned scenes to be succeeded")
    artifact = await assemble_render_job_artifacts(job, scenes)
    lineage = record_final_render_artifact(
        db,
        job=job,
        artifact=artifact,
        lineage_kind="rerender_reassembly",
        rerender_reason=rerender_reason or "smart_reassembly",
        affected_scene_indexes=affected_scene_indexes or [],
        metadata={"source": "smart_reassembly"},
        commit=False,
    )
    job.final_video_url = artifact.final_video_url
    job.final_video_path = artifact.final_video_path
    job.output_url = artifact.final_video_url
    job.output_path = artifact.final_video_path
    job.final_timeline = artifact.timeline
    job.status = "completed"
    db.commit()

    run_media_qa_for_render_artifact(
        db,
        project_id=job.project_id,
        render_job_id=job.id,
        final_video_url=artifact.final_video_url,
        artifact_id=lineage.artifact_id,
        artifact_checksum=artifact.sha256,
        created_by="rerender-smart-reassembly",
    )

    return {
        "render_job_id": render_job_id,
        "affected_scene_indexes": affected_scene_indexes or [],
        "final_video_url": artifact.final_video_url,
        "final_video_path": artifact.final_video_path,
        "sha256": artifact.sha256,
        "size_bytes": artifact.size_bytes,
        "lineage_id": lineage.id,
        "parent_artifact_id": lineage.parent_artifact_id,
        "previous_final_checksum": lineage.previous_final_checksum,
    }
