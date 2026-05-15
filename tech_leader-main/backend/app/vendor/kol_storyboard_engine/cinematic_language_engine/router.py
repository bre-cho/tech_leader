from fastapi import APIRouter
from .schemas import CinematicRequest
from .planner import build_cinematic_storyboard
from .technique_library import build_150_technique_library

router = APIRouter(prefix="/api/cinematic-language", tags=["Cinematic Language Engine"])

@router.get("/techniques")
def list_techniques():
    techniques = build_150_technique_library()
    return {"count": len(techniques), "techniques": [t.model_dump() for t in techniques]}

@router.post("/build-storyboard")
def build_storyboard(req: CinematicRequest):
    storyboard = build_cinematic_storyboard(req)
    return {"status": "ok", "storyboard": storyboard.model_dump()}
