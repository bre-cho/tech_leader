from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.render_production import ProductionRenderOrchestrator, RenderProductionError

router = APIRouter(prefix="/api/render-production", tags=["Production Render"])


class ProductionRenderExecuteRequest(BaseModel):
    render_package: Dict[str, Any] = Field(default_factory=dict)
    scene_video_paths: List[str]
    voice_audio_path: Optional[str] = None
    bgm_path: Optional[str] = None
    sfx_paths: List[str] = Field(default_factory=list)
    subtitle_path: Optional[str] = None
    job_id: Optional[str] = None


@router.post("/execute")
def execute_production_render(req: ProductionRenderExecuteRequest):
    try:
        return ProductionRenderOrchestrator().execute(
            render_package=req.render_package,
            scene_video_paths=req.scene_video_paths,
            voice_audio_path=req.voice_audio_path,
            bgm_path=req.bgm_path,
            sfx_paths=req.sfx_paths,
            subtitle_path=req.subtitle_path,
            job_id=req.job_id,
        )
    except RenderProductionError as e:
        raise HTTPException(status_code=422, detail=str(e))
