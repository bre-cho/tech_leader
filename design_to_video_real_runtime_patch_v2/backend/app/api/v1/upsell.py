from fastapi import APIRouter
from typing import Any, Dict
from app.agents.runtime import TechnicalLeadRuntime

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/upsell", tags=["upsell"])


@router.post("/analyze")
def analyze_upsell(payload: Dict[str, Any]):
    project_id, trace_id = require_project_and_trace(payload)
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data["upsell"],
        step="upsell.analyzed",
    )
