from __future__ import annotations

from fastapi import APIRouter
from app.smart_subtitle_engine.schemas import SmartSubtitleRequest
from app.smart_subtitle_engine.service import SmartSubtitleService

router = APIRouter(prefix="/api/subtitles", tags=["P17 Smart Subtitle Engine"])


@router.post("/smart-package")
def build_smart_subtitle_package(req: SmartSubtitleRequest):
    return SmartSubtitleService().build(req)
