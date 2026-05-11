"""Admin API: circuit breaker management endpoints.

Endpoints
---------
GET  /admin/circuit-breakers          — Snapshot of all known provider breakers.
POST /admin/circuit-breakers/{p}/reset — Reset a single breaker to CLOSED.
POST /admin/circuit-breakers/reset-all — Reset all cached breakers to CLOSED.

These endpoints are protected by the ``admin:circuit-breakers`` permission so
they require a valid bearer token when ``AUTH_ENABLED=true``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_permission
from app.services.provider_routing.circuit_breaker import (
    get_breaker,
    invalidate_breaker_cache,
    KNOWN_PROVIDERS,
)

router = APIRouter(prefix="/admin/circuit-breakers", tags=["admin"])

# Known production providers — breaker snapshots are always surfaced for these.
_KNOWN_PROVIDERS = KNOWN_PROVIDERS

_auth = Depends(require_permission("admin:circuit-breakers"))


@router.get(
    "",
    summary="List circuit breaker states for all known providers",
    dependencies=[_auth],
)
def list_circuit_breakers() -> dict:
    """Return a snapshot of each provider's circuit breaker state.

    Fields per provider
    -------------------
    ``state``          : ``CLOSED`` | ``OPEN`` | ``HALF_OPEN``
    ``failures``       : Consecutive failure count.
    ``tripped_at``     : Unix timestamp when the circuit was last tripped (or ``null``).
    ``redis_available``: Whether Redis is reachable for this breaker.
    """
    return {
        "providers": {
            p: get_breaker(p).get_state()
            for p in _KNOWN_PROVIDERS
        }
    }


@router.post(
    "/{provider}/reset",
    summary="Reset a single provider's circuit breaker to CLOSED",
    dependencies=[_auth],
)
def reset_circuit_breaker(provider: str) -> dict:
    """Reset *provider*'s circuit breaker to ``CLOSED`` and clear the failure counter.

    Use this after confirming a provider has recovered from an outage, to
    allow traffic through without waiting for the auto-recovery timeout.
    """
    normalized = provider.strip().lower()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="provider must not be empty",
        )
    breaker = get_breaker(normalized)
    breaker.record_success()  # record_success resets to CLOSED
    invalidate_breaker_cache(normalized)
    return {
        "provider": normalized,
        "action": "reset",
        "state": get_breaker(normalized).get_state(),
    }


@router.post(
    "/reset-all",
    summary="Reset all cached circuit breakers to CLOSED",
    dependencies=[_auth],
)
def reset_all_circuit_breakers() -> dict:
    """Reset every cached circuit breaker to ``CLOSED``.

    Use with caution — resetting all breakers simultaneously means unhealthy
    providers will receive traffic again immediately.  Prefer per-provider
    resets when possible.
    """
    for p in _KNOWN_PROVIDERS:
        get_breaker(p).record_success()
    invalidate_breaker_cache()
    return {
        "action": "reset-all",
        "providers_reset": _KNOWN_PROVIDERS,
    }
