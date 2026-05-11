from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict

from app.agents.runtime import TechnicalLeadRuntime

router = APIRouter(prefix="/design", tags=["design"])


class DesignGenerateRequest(BaseModel):
    industry: str
    product: str
    target_customer: str | None = None
    channel: str = "Facebook"
    goal: str = "sales"
    pain_point: str | None = None
    selling_angle: str | None = None


class DesignSelectRequest(BaseModel):
    project_id: str
    selected_variant_id: str | None = None
    selected_variant: Dict[str, Any]
    channel: str = "Facebook"
    product: str
    industry: str
    product_type: str = "physical"


@router.post("/generate")
def generate_design(payload: DesignGenerateRequest):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_phase1(payload.model_dump())
    return {"ok": True, "data": data, "audit": runtime.audit_snapshot()}


@router.post("/score")
def score_design(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_phase1(payload)
    return {"ok": True, "data": data, "audit": runtime.audit_snapshot()}


@router.post("/select")
def select_design(payload: DesignSelectRequest):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload.model_dump())
    return {"ok": True, "data": data, "audit": runtime.audit_snapshot()}
