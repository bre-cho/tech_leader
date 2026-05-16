"""
Backend route for Seedance 2.0 / kie.ai connectivity check.

POST /api/v1/seedance/test-connection
    Validates SEEDANCE_API_KEY by calling a lightweight kie.ai endpoint.
    Returns { success, detail } — no key is ever returned to the caller.

Security:
    - SEEDANCE_API_KEY is read ONLY from backend env (backend/.env or system env).
    - This endpoint does NOT accept an API key as input.
    - The frontend calls this route; the backend calls kie.ai.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.vendor.seedance2.config import seedance_config

router = APIRouter(prefix="/seedance", tags=["seedance"])


class TestConnectionRequest(BaseModel):
    account_id: str | None = None  # informational only, not used for auth


@router.post("/test-connection")
def test_connection(payload: TestConnectionRequest | None = None):
    """
    Verify that SEEDANCE_API_KEY can reach the kie.ai API.
    Returns { success: bool, detail: str }.
    """
    if not seedance_config.is_configured():
        return {
            "success": False,
            "detail": (
                "SEEDANCE_API_KEY is not set in backend environment. "
                "Add it to backend/.env and restart the backend."
            ),
        }

    headers = {
        "Authorization": f"Bearer {seedance_config.api_key}",
        "Content-Type": "application/json",
    }
    test_url = f"{seedance_config.api_base_url}/api/v1/user/me"

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(test_url, headers=headers)

        if resp.is_success:
            return {"success": True, "detail": "Connection OK", "provider": seedance_config.provider_label}
        else:
            return {
                "success": False,
                "status": resp.status_code,
                "detail": resp.text[:300],
            }
    except httpx.RequestError as exc:
        return {"success": False, "detail": f"Network error: {exc}"}


@router.get("/config-status")
def config_status():
    """
    Return sanitized config status — never exposes the actual key.
    """
    return {
        "configured": seedance_config.is_configured(),
        "provider": seedance_config.provider_label,
        "api_base_url": seedance_config.api_base_url,
        "model": seedance_config.model,
        "render_mode": "sequential",
        "max_concurrent_render": 1,
    }
