from __future__ import annotations

from fastapi import APIRouter

from app.providers.kling.health import check_kling_config


router = APIRouter(prefix="/v1/providers/kling", tags=["providers-kling"])


@router.get("/health")
def kling_health():
    return check_kling_config()
