from __future__ import annotations

from app.core.config import settings
from app.providers.common import ProviderConfigError


def get_runway_api_secret() -> str:
    """
    Official Runway API auth helper.

    Official env:
      RUNWAYML_API_SECRET=key_...

    Backward compatible fallback:
      RUNWAY_API_KEY
    """
    secret = (
        getattr(settings, "runwayml_api_secret", None)
        or getattr(settings, "runway_api_key", None)
    )
    if not secret:
        raise ProviderConfigError("RUNWAYML_API_SECRET is required for Runway provider")
    return secret


def runway_headers() -> dict[str, str]:
    """
    Runway REST API header contract.

    Keep API version configurable because Runway API versions may advance.
    """
    headers = {
        "Authorization": f"Bearer {get_runway_api_secret()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    api_version = getattr(settings, "runway_api_version", None)
    if api_version:
        headers["X-Runway-Version"] = api_version

    return headers
