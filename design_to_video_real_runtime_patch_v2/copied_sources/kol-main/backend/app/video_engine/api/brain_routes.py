from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from ..brain.orchestrator import VideoBrainOrchestrator

router = APIRouter(prefix="/video/brain", tags=["video-brain"])


class BrainPlanRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    mode: str = "text_to_video"
    provider: str = "auto"
    routing_profile: str = "cinematic_ads"
    aspect_ratio: str = "16:9"
    duration_seconds: int = 8
    quality_tier: str = "standard"
    seed: int | None = None
    reference_image_url: str | None = None
    reference_video_url: str | None = None
    negative_prompt: str | None = None
    audio: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _get_orchestrator(db: Session = Depends(get_db)) -> VideoBrainOrchestrator:
    """FastAPI dependency that creates a per-request :class:`VideoBrainOrchestrator`.

    Passes the active DB session so :class:`~app.video_engine.brain.learning_loop.LearningLoopStore`
    uses the DB backend in production (the file backend raises ``RuntimeError``
    when ``is_production_env()`` is ``True``).
    """
    return VideoBrainOrchestrator(db=db)


@router.post("/plan")
def plan_video(
    request: BrainPlanRequest,
    orchestrator: VideoBrainOrchestrator = Depends(_get_orchestrator),
) -> Dict[str, Any]:
    return orchestrator.plan(request.model_dump())


@router.post("/outcome")
def record_outcome(
    outcome: Dict[str, Any],
    orchestrator: VideoBrainOrchestrator = Depends(_get_orchestrator),
) -> Dict[str, Any]:
    return {"updated": orchestrator.record_outcome(outcome)}
