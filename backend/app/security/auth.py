from __future__ import annotations

from fastapi import HTTPException, Request, status
from app.config import settings


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
EXEMPT_WRITE_PATHS = {"/api/v1/health", "/api/v1/governance/operating-law"}


def cors_origins() -> list[str]:
    return [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]


def _configured_write_keys() -> set[str]:
    return {key.strip() for key in settings.write_api_keys.split(",") if key.strip()}


def write_auth_enforced() -> bool:
    env = (settings.app_env or "").lower()
    production_like = env in {"production", "staging"}
    return settings.require_write_auth or (settings.strict_mode and production_like)


def assert_write_auth_configured() -> None:
    if write_auth_enforced() and not _configured_write_keys():
        raise RuntimeError("WRITE_API_KEYS is required when write-route authentication is enforced")


def _extract_auth_token(request: Request) -> str:
    api_key = request.headers.get("x-api-key")
    if api_key:
        return api_key.strip()
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return ""


def enforce_write_route_auth(request: Request) -> None:
    if request.method.upper() not in WRITE_METHODS:
        return
    if not request.url.path.startswith("/api/v1"):
        return
    if request.url.path in EXEMPT_WRITE_PATHS:
        return
    if not write_auth_enforced():
        return

    token = _extract_auth_token(request)
    allowed = _configured_write_keys()
    if not token or token not in allowed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid write-route credentials",
        )
