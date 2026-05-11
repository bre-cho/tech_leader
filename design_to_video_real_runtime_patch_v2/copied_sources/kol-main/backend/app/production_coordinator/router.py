
from __future__ import annotations

from fastapi import APIRouter

from .executor import GraphProductionCoordinator
from .planner import build_production_plan
from .schemas import ProductionInput

router = APIRouter(prefix="/api/production-coordinator", tags=["Production Coordinator"])


@router.post("/plan")
def plan(req: ProductionInput):
    production_plan = build_production_plan(req)
    return production_plan.model_dump()


@router.post("/run")
def run(req: ProductionInput):
    production_plan = build_production_plan(req)
    result = GraphProductionCoordinator().run(req, production_plan)
    return {
        "plan": production_plan.model_dump(),
        "result": result.model_dump(),
    }


@router.get("/closed-loop-contract")
def closed_loop_contract():
    return {
        "principle": "RenderPackage is only a plan. ProductionCoordinator must drive modules until FinalVideoContract exists.",
        "closed_loop": [
            "Input",
            "Code Intelligence Graph",
            "Storyboard",
            "Multi-Angle",
            "Higgsfield/Seedance2",
            "Provider Payload",
            "Provider or HTML Render",
            "Audio",
            "Subtitle",
            "FFmpeg Assembly",
            "Artifact Storage",
            "FinalVideoContract",
            "Analytics Feedback",
        ],
        "hard_rules": [
            "NO_GRAPH -> LIMITED_COORDINATION",
            "NO_STORYBOARD -> NO_RENDER_PACKAGE",
            "NO_PROVIDER_PAYLOAD_AND_NO_HTML_SCENE -> NO_SCENE_RENDER",
            "NO_AUDIO -> NO_FINAL_EXPORT",
            "NO_SUBTITLE_SAFE_ZONE -> NO_BURN_IN",
            "NO_FINAL_MP4 -> FAIL_CONTRACT",
            "NO_FINAL_VIDEO_CONTRACT -> NO_DOWNLOAD",
        ],
    }
