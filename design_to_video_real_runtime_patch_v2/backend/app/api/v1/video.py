from fastapi import APIRouter
from typing import Any, Dict
from app.agents.runtime import TechnicalLeadRuntime

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/concept")
def create_video_concept(payload: Dict[str, Any]):
    project_id, trace_id = require_project_and_trace(payload)
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data["video_concept"],
        step="video.concept.generated",
    )


@router.post("/storyboard")
def create_storyboard(payload: Dict[str, Any]):
    project_id, trace_id = require_project_and_trace(payload)
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data["storyboard"],
        step="storyboard.generated",
    )
