from __future__ import annotations

from fastapi import APIRouter
from app.storyboard_engine.schemas import PosterInput, StoryboardResponse
from app.storyboard_engine.service import AutoStoryboardService

router = APIRouter(prefix="/api/storyboard", tags=["Auto Storyboard Engine V2"])
service = AutoStoryboardService()


@router.post("/generate-v2", response_model=StoryboardResponse)
def generate_storyboard_v2(payload: PosterInput) -> StoryboardResponse:
    return service.run(payload)


@router.post("/render-ready", response_model=StoryboardResponse)
def render_ready(payload: PosterInput) -> StoryboardResponse:
    return service.run(payload)
