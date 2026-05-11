from __future__ import annotations

import time
from typing import Any

import jwt

from app.core.config import settings
from app.providers.common import ProviderConfigError


def generate_kling_jwt(
    access_key: str | None = None,
    secret_key: str | None = None,
    ttl_seconds: int | None = None,
) -> str:
    """
    Official Kling API authentication helper.

    Kling API uses:
      AccessKey + SecretKey -> JWT -> Authorization: Bearer <token>

    Required JWT claims:
      iss: access key
      exp: expiration timestamp
      nbf: not-before timestamp

    The token is intentionally short-lived. Default: 1800 seconds.
    """
    ak = access_key or getattr(settings, "kling_access_key", None)
    sk = secret_key or getattr(settings, "kling_secret_key", None)
    ttl = ttl_seconds or getattr(settings, "kling_jwt_ttl_seconds", 1800)

    if not ak:
        raise ProviderConfigError("KLING_ACCESS_KEY is required")
    if not sk:
        raise ProviderConfigError("KLING_SECRET_KEY is required")

    now = int(time.time())
    payload: dict[str, Any] = {
        "iss": ak,
        "exp": now + int(ttl),
        "nbf": now - 5,
    }

    return jwt.encode(payload, sk, algorithm="HS256")
