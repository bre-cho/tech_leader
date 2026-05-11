from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.real_image_provider_bridge import RealImageProviderBridge
from app.services.real_video_render_bridge import RealVideoRenderBridge

router = APIRouter(prefix="/api/v1/real-pipeline", tags=["design-to-video-real-pipeline"])


class GenerateRealDesignRequest(BaseModel):
    industry: str
    product: str
    goal: str
    channel: str = "facebook"
    target_customer: str | None = None
    count: int = Field(default=3, ge=1, le=5)


class CreateRealVideoRequest(BaseModel):
    project_id: str | None = None
    provider: str | None = None
    source_image_url: str | None = None
    aspect_ratio: str = "9:16"
    subtitle_mode: str = "burn"
    storyboard: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/design/generate-real")
async def generate_real_design(payload: GenerateRealDesignRequest) -> dict[str, Any]:
    diagnosis = payload.model_dump()
    bridge = RealImageProviderBridge()
    try:
        variants = await bridge.generate_design_variants(diagnosis=diagnosis, count=payload.count)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"real image generation failed: {exc}") from exc
    return {
        "project_id": str(uuid4()),
        "mode": "real_image_provider",
        "variants": variants,
    }


@router.post("/video/render-real")
async def render_real_video(payload: CreateRealVideoRequest) -> dict[str, Any]:
    if not payload.storyboard:
        raise HTTPException(status_code=422, detail="storyboard is required")
    bridge = RealVideoRenderBridge()
    try:
        result = await bridge.create_render_job_from_storyboard(
            project_id=payload.project_id or str(uuid4()),
            storyboard=payload.storyboard,
            source_image_url=payload.source_image_url,
            provider=payload.provider,
            aspect_ratio=payload.aspect_ratio,
            subtitle_mode=payload.subtitle_mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"real video render submit failed: {exc}") from exc
    return result
