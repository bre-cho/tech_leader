
from __future__ import annotations

from fastapi import APIRouter
from .schemas import MultiAngleRequest
from .multi_angle_planner import build_single_image_multi_angle_storyboard
from .quality_gate import validate_multi_angle_storyboard

router = APIRouter(prefix="/api/storyboard-production", tags=["Storyboard Production"])


@router.post("/single-image-multi-angle")
def single_image_multi_angle(req: MultiAngleRequest):
    storyboard = build_single_image_multi_angle_storyboard(req)
    gate = validate_multi_angle_storyboard(storyboard)
    return {
        "storyboard": storyboard.model_dump(),
        "quality_gate": gate,
        "next_step": "send storyboard.render_package_patch to ProductionRenderOrchestrator"
    }
