from fastapi import APIRouter
from typing import Any, Dict
from app.agents.runtime import TechnicalLeadRuntime

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/concept")
def create_video_concept(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return {"ok": True, "data": data["video_concept"], "audit": runtime.audit_snapshot()}


@router.post("/storyboard")
def create_storyboard(payload: Dict[str, Any]):
    runtime = TechnicalLeadRuntime()
    data = runtime.run_after_image_selected(payload)
    return {"ok": True, "data": data["storyboard"], "audit": runtime.audit_snapshot()}
