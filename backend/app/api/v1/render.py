from __future__ import annotations

from typing import Dict

from fastapi import APIRouter

from app.schemas.design_to_video import RenderProjectRequest

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/render", tags=["render"])


@router.post("/project")
def create_render_project(payload: RenderProjectRequest) -> Dict[str, object]:
    body = payload.model_dump()
    project_id, trace_id = require_project_and_trace(body)
    storyboard = body.get("storyboard", [])
    data = {
        "render_project_created": True,
        "provider": body.get("provider", "adapter"),
        "scene_count": len(storyboard),
        "status": "queued",
    }
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data,
        step="render.project.created",
    )
