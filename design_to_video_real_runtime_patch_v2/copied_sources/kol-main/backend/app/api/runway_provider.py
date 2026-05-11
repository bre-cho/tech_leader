from __future__ import annotations

from fastapi import APIRouter

from app.providers.runway.health import check_runway_config


router = APIRouter(prefix="/v1/providers/runway", tags=["providers-runway"])


@router.get("/health")
def runway_health():
    return check_runway_config()
