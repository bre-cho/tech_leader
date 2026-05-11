from __future__ import annotations

from app.providers.common import ProviderConfigError
from app.providers.kling.auth import generate_kling_jwt


def check_kling_config() -> dict:
    """
    Lightweight healthcheck:
    - verifies env exists
    - verifies JWT can be generated
    Does not spend provider credits.
    """
    try:
        token = generate_kling_jwt()
        return {
            "provider": "kling",
            "configured": True,
            "jwt_generated": bool(token),
            "auth_mode": "access_key_secret_jwt",
        }
    except ProviderConfigError as exc:
        return {
            "provider": "kling",
            "configured": False,
            "jwt_generated": False,
            "auth_mode": "access_key_secret_jwt",
            "error": str(exc),
        }
