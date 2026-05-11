"""Render job worker entrypoints."""
from app.core.database import SessionLocal
from app.services.project_render_runtime import trigger_project_render
from app.services.render_queue import enqueue_render_dispatch
from app.services.render_repository import build_render_job_response, get_render_job_by_id


def process_render_job(job: dict) -> dict:
    with SessionLocal() as db:
        render_job_id = str(job.get("render_job_id") or job.get("id") or "").strip()
        project_id = str(job.get("project_id") or "").strip()

        if render_job_id:
            existing = get_render_job_by_id(db, render_job_id, with_scenes=False)
            if existing is None:
                return {
                    "status": "error",
                    "error": "render_job_not_found",
                    "render_job_id": render_job_id,
                    "job": job,
                }

            dispatch = enqueue_render_dispatch(existing.id)
            snapshot = build_render_job_response(db, existing, include_scenes=True)
            return {
                "status": "queued",
                "render_job_id": existing.id,
                "dispatch": dispatch,
                "render_status": snapshot.status,
                "job": job,
            }

        if project_id:
            created = trigger_project_render(db, project_id)
            created_job_id = str(created.get("render_job_id") or "").strip()
            created_job = get_render_job_by_id(db, created_job_id, with_scenes=False) if created_job_id else None
            snapshot = build_render_job_response(db, created_job, include_scenes=True) if created_job else None
            return {
                "status": "queued",
                "project_id": project_id,
                "render_job_id": created_job_id,
                "render_status": snapshot.status if snapshot else created.get("status", "queued"),
                "job": job,
            }

        return {
            "status": "error",
            "error": "missing_render_job_id_or_project_id",
            "job": job,
        }
