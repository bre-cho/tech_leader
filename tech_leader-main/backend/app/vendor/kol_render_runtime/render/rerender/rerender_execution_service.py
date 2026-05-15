from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.async_utils import run_async
from app.models.render_job import RenderJob
from app.models.render_scene_task import RenderSceneTask
from app.render.rerender.dependency_graph import build_rerender_dependency_graph
from app.render.rerender.media_rebuild_service import RerenderMediaRebuildService
from app.render.rerender.smart_reassembly import smart_reassemble_render_job
from app.render.rerender.timeline_drift_guard import validate_timeline_drift
from app.workers.render_tasks import render_dispatch_task


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RerenderExecutionService:
    """Production rerender path backed by RenderJob/RenderSceneTask.

    It marks impacted scenes as queued, preserves dependency impact metadata,
    dispatches provider execution again, and optionally triggers smart assembly
    when all scenes are already succeeded.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def rerender_scene(
        self,
        *,
        render_job_id: str,
        scene_index: int,
        change_type: str = "both",
        override_payload: dict[str, Any] | None = None,
        force: bool = False,
        smart_reassemble_if_ready: bool = True,
    ) -> dict[str, Any]:
        job = self.db.query(RenderJob).filter(RenderJob.id == render_job_id).first()
        if job is None:
            raise ValueError(f"RenderJob {render_job_id} not found")
        timeline = job.final_timeline if isinstance(job.final_timeline, dict) else None
        if timeline is None and job.final_timeline_json:
            try:
                timeline = json.loads(job.final_timeline_json)
            except json.JSONDecodeError:
                timeline = None

        impact = build_rerender_dependency_graph(timeline=timeline, changed_scene_index=scene_index, change_type=change_type)
        scenes = (
            self.db.query(RenderSceneTask)
            .filter(RenderSceneTask.job_id == render_job_id, RenderSceneTask.scene_index.in_(impact.affected_scene_indexes))
            .all()
        )
        if not scenes:
            raise ValueError("No affected scenes found for rerender")

        drift_reports = []
        media_rebuilds = []
        media_rebuilder = RerenderMediaRebuildService(self.db)
        for scene in scenes:
            payload = {}
            try:
                payload = json.loads(scene.request_payload_json or "{}")
            except json.JSONDecodeError:
                payload = {}
            old_duration = payload.get("duration") or payload.get("duration_sec")
            if override_payload:
                payload.update(override_payload)
            new_duration = payload.get("duration") or payload.get("duration_sec")
            drift = validate_timeline_drift(old_duration_sec=old_duration, new_duration_sec=new_duration)
            drift_reports.append(drift.__dict__ | {"scene_index": scene.scene_index})
            if not drift.ok and not force:
                raise ValueError(f"Timeline drift exceeds budget for scene {scene.scene_index}: {drift.duration_delta_ms}ms")
            media_rebuilds.append(
                media_rebuilder.rebuild_for_scene(
                    job=job,
                    scene=scene,
                    change_type=change_type,
                    override_payload=payload,
                )
            )
            scene.status = "queued"
            scene.request_payload_json = json.dumps(payload, ensure_ascii=False, default=str)
            scene.output_video_url = None
            scene.local_video_path = None
            scene.error_message = None
            scene.failure_code = None
            scene.failure_category = None
            scene.retry_count = 0
            scene.provider_task_id = None
            scene.provider_operation_name = None
            scene.provider_status_raw = None
            scene.manual_retry_requested_at = _now()

        job.status = "queued"
        job.error_message = None
        job.completed_at = None
        job.completed_scene_count = max(0, int(job.completed_scene_count or 0) - len(scenes))
        self.db.commit()

        render_dispatch_task.delay(render_job_id)
        reassembly = None
        if smart_reassemble_if_ready:
            current = (
                self.db.query(RenderSceneTask)
                .filter(RenderSceneTask.job_id == render_job_id, RenderSceneTask.status == "succeeded")
                .count()
            )
            if current >= int(job.planned_scene_count or 0):
                reassembly = run_async(
                    smart_reassemble_render_job(
                        self.db,
                        render_job_id,
                        impact.affected_scene_indexes,
                        rerender_reason=f"rerender_scene:{change_type}:scene_{scene_index}",
                    )
                )

        return {
            "ok": True,
            "render_job_id": render_job_id,
            "changed_scene_index": scene_index,
            "change_type": change_type,
            "affected_scene_indexes": impact.affected_scene_indexes,
            "dependency_reason": impact.reason,
            "drift_reports": drift_reports,
            "media_rebuilds": media_rebuilds,
            "dispatched": True,
            "smart_reassembly": reassembly,
        }
