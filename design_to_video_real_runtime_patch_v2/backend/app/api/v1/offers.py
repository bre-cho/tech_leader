from fastapi import APIRouter
from typing import Any, Dict
from app.agents.runtime import TechnicalLeadRuntime

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("/recommend")
def recommend_offer(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return {"ok": True, "data": data["offer"], "audit": runtime.audit_snapshot()}
