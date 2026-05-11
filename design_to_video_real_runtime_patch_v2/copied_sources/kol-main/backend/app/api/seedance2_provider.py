from __future__ import annotations

import os

from fastapi import APIRouter

router = APIRouter(prefix="/v1/providers/seedance2", tags=["providers-seedance2"])


@router.get("/health")
def seedance2_health():
    """Check Seedance2 provider configuration and credential presence."""
    api_key = os.getenv("SEEDANCE2_API_KEY", "").strip()
    base_url = os.getenv("SEEDANCE2_BASE_URL", "").strip()

    configured = bool(api_key and base_url)
    status = "ready" if configured else "unconfigured"
    missing: list[str] = []
    if not api_key:
        missing.append("SEEDANCE2_API_KEY")
    if not base_url:
        missing.append("SEEDANCE2_BASE_URL")

    return {
        "provider": "seedance2",
        "registered": True,
        "status": status,
        "configured": configured,
        "missing_env": missing,
    }


@router.get("/capabilities")
def seedance2_capabilities():
    return {
        "provider": "seedance2",
        "modes": [
            "text_to_video",
            "image_to_video",
            "reference_image_to_video",
        ],
        "recommended": [
            "short-form vertical video ads",
            "motion-heavy before-after creatives",
            "fast variant generation",
        ],
    }
