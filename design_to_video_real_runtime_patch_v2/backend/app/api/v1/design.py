from fastapi import APIRouter
from fastapi import HTTPException
from typing import Any, Dict
from uuid import uuid4

from app.agents.runtime import TechnicalLeadRuntime
from app.schemas.design_to_video import DesignGenerateRequest, DesignSelectRequest

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/design", tags=["design"])


@router.post("/generate")
def generate_design(payload: DesignGenerateRequest):
    runtime = TechnicalLeadRuntime()
    request = payload.model_dump()
    request["trace_id"] = request.get("trace_id") or str(uuid4())
    data = runtime.run_phase1(request)
    return standard_response(
        project_id=data["project_id"],
        trace_id=data["trace_id"],
        data=data,
        step="image.scored",
    )


@router.post("/score")
def score_design(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    if not payload.get("project_id"):
        payload["project_id"] = str(uuid4())
    if not payload.get("trace_id"):
        payload["trace_id"] = str(uuid4())
    data = runtime.run_phase1(payload)
    return standard_response(
        project_id=data["project_id"],
        trace_id=data["trace_id"],
        data={"image_variants": data.get("image_variants", [])},
        step="image.scored",
    )


@router.post("/select")
def select_design(payload: DesignSelectRequest):
    runtime = TechnicalLeadRuntime()
    body = payload.model_dump()
    project_id, trace_id = require_project_and_trace(body)
    if not body.get("selected_variant"):
        raise HTTPException(status_code=400, detail="selected_variant is required")
    selected_scores = body["selected_variant"].get("scores")
    if isinstance(selected_scores, dict):
        body["scores"] = selected_scores
    data = runtime.run_after_image_selected(body)
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data,
        step="winner_dna.saved",
    )
