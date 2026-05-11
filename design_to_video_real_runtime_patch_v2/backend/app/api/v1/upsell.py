from fastapi import APIRouter
from typing import Any, Dict
from app.agents.runtime import TechnicalLeadRuntime

router = APIRouter(prefix="/upsell", tags=["upsell"])


@router.post("/analyze")
def analyze_upsell(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return {"ok": True, "data": data["upsell"], "audit": runtime.audit_snapshot()}
