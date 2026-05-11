from __future__ import annotations

from app.providers.common import ProviderConfigError
from app.providers.runway.auth import get_runway_api_secret


def check_runway_config() -> dict:
    """
    Lightweight Runway healthcheck:
    - verifies RUNWAYML_API_SECRET exists
    - does not spend credits
    """
    try:
        secret = get_runway_api_secret()
        return {
            "provider": "runway",
            "configured": True,
            "auth_mode": "RUNWAYML_API_SECRET",
            "secret_prefix": secret[:6] + "..." if len(secret) > 6 else "***",
        }
    except ProviderConfigError as exc:
        return {
            "provider": "runway",
            "configured": False,
            "auth_mode": "RUNWAYML_API_SECRET",
            "error": str(exc),
        }
