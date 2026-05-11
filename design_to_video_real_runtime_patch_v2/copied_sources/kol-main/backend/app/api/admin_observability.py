"""Admin observability endpoints — drama engine placeholders and learning loop signals.

Endpoints
---------
GET /admin/observability/drama-engines
    Returns the placeholder status of each drama ML engine.  A ``placeholder=true``
    value means the engine is running heuristic logic instead of a trained model.
    The response is also available in Prometheus text format when the
    ``Accept: text/plain`` header is sent, enabling scraping by a custom exporter.

GET /admin/observability/learning-loop
    Returns whether the learning loop is active or silently dropping signals due
    to the NoOp backend being selected (Redis/DB unavailable or staging env).

These endpoints require the ``admin:observability`` permission when
``AUTH_ENABLED=true``.
"""
from __future__ import annotations

import importlib
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from app.auth.dependencies import require_permission

router = APIRouter(prefix="/admin/observability", tags=["admin"])
_logger = logging.getLogger(__name__)

_auth = Depends(require_permission("admin:observability"))

# ---------------------------------------------------------------------------
# Drama engine module cache — loaded once per process so repeated requests to
# /drama-engines do not pay the importlib overhead on every call.
# ---------------------------------------------------------------------------
_DRAMA_ENGINE_SPECS: list[tuple[str, str, str]] = [
    ("tension", "app.drama.engines.tension_engine", "is_tension_engine_placeholder"),
    ("memory_recall", "app.drama.engines.memory_recall_engine", "is_memory_recall_engine_placeholder"),
    ("character_intent", "app.drama.engines.character_intent_engine", "is_character_intent_engine_placeholder"),
    ("subtext", "app.drama.engines.subtext_engine", "is_subtext_engine_placeholder"),
]

# Pre-cache the module + callable references; fall back to lazy import on error.
_DRAMA_ENGINE_FNS: dict[str, Any] = {}

for _engine, _mod_path, _fn_name in _DRAMA_ENGINE_SPECS:
    try:
        _mod = importlib.import_module(_mod_path)
        _DRAMA_ENGINE_FNS[_engine] = getattr(_mod, _fn_name)
    except Exception as _exc:  # noqa: BLE001
        _logger.warning("admin_observability: could not pre-import %s.%s: %s", _mod_path, _fn_name, _exc)
        _DRAMA_ENGINE_FNS[_engine] = None


@router.get(
    "/drama-engines",
    summary="Drama ML engine placeholder status",
    dependencies=[_auth],
    response_model=None,
)
def drama_engine_placeholders(request: Request):
    """Return placeholder status for each drama ML engine.

    A placeholder engine is running heuristic logic because no trained model
    artifact has been configured via the corresponding ``DRAMA_*_MODEL_PATH``
    environment variable.  All four placeholders being ``true`` in production
    is a signal that ML drama quality has not been activated.

    Prometheus text format
    ----------------------
    Set ``Accept: text/plain`` to receive Prometheus exposition format::

        # HELP drama_engine_placeholder 1 if the engine uses heuristic fallback
        # TYPE drama_engine_placeholder gauge
        drama_engine_placeholder{engine="tension"} 1
        drama_engine_placeholder{engine="memory_recall"} 1
        drama_engine_placeholder{engine="character_intent"} 1
        drama_engine_placeholder{engine="subtext"} 1
    """
    statuses: dict[str, bool] = {}
    errors: dict[str, str] = {}

    for engine, _mod_path, _fn_name in _DRAMA_ENGINE_SPECS:
        fn = _DRAMA_ENGINE_FNS.get(engine)
        if fn is None:
            # Module failed to pre-import; attempt a lazy import as a last resort.
            try:
                mod = importlib.import_module(_mod_path)
                fn = getattr(mod, _fn_name)
                _DRAMA_ENGINE_FNS[engine] = fn
            except Exception as exc:  # noqa: BLE001
                statuses[engine] = True  # assume placeholder when we cannot check
                errors[engine] = str(exc)
                continue
        try:
            statuses[engine] = bool(fn())
        except Exception as exc:  # noqa: BLE001
            statuses[engine] = True
            errors[engine] = str(exc)

    accept = request.headers.get("accept", "")
    if "text/plain" in accept:
        lines = [
            "# HELP drama_engine_placeholder 1 if the engine uses heuristic fallback, 0 if model is active",
            "# TYPE drama_engine_placeholder gauge",
        ]
        for engine, is_placeholder in statuses.items():
            lines.append(f'drama_engine_placeholder{{engine="{engine}"}} {1 if is_placeholder else 0}')
        return PlainTextResponse("\n".join(lines) + "\n")

    return {
        "engines": {
            engine: {
                "placeholder": is_placeholder,
                "model_active": not is_placeholder,
            }
            for engine, is_placeholder in statuses.items()
        },
        "all_placeholders": all(statuses.values()),
        "errors": errors or None,
    }


@router.get(
    "/learning-loop",
    summary="Learning loop signal status",
    dependencies=[_auth],
)
def learning_loop_status() -> dict:
    """Return whether the learning loop is collecting real signals or dropping them.

    ``noop_backend_active=true`` means learning signals are silently discarded.
    This happens when:
    - Redis is unavailable and no DB session is available (dev/CI environments).
    - The worker is running in staging and the staging NoOp backend was selected.

    ``staging_noop_backend_active=true`` for more than 24 hours indicates a
    staging misconfiguration (DB session missing or Redis unreachable).

    Alert rule suggestion
    ---------------------
    Trigger a severity-2 alert when ``staging_noop_backend_active=true``
    persists for longer than 24 hours or ``noop_backend_active=true`` in
    production.
    """
    result: dict = {}
    try:
        from app.video_engine.brain.learning_loop import (  # noqa: PLC0415
            noop_backend_active,
            staging_noop_backend_active,
        )
        result["noop_backend_active"] = noop_backend_active
        result["staging_noop_backend_active"] = staging_noop_backend_active
        result["signals_collected"] = not noop_backend_active
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
        result["noop_backend_active"] = None
        result["staging_noop_backend_active"] = None
        result["signals_collected"] = None
    return result
