from __future__ import annotations

import importlib
import logging
import os

from fastapi import FastAPI

log = logging.getLogger(__name__)

# Populated by _import_router() for any module that fails to load.
# Exposed via get_skipped_routers() so a /health or /startup endpoint can
# surface partial-registration failures to ops without crashing the process.
_skipped_routers: list[dict[str, str]] = []
_CRITICAL_ROUTERS: set[tuple[str, str]] = {
    ("app.api.storyboard_routes", "router"),
    ("app.api.poster_video_render_routes", "router"),
    ("app.api.production_render_routes", "router"),
    ("app.api.smart_subtitle_routes", "router"),
    ("app.api.provider_callbacks", "router"),
    ("app.api.render_execution", "router"),
    ("app.api.render_job_health", "router"),
    ("app.api.render_job_status", "router"),
    ("app.api.video_router", "router"),
    ("app.api.seedance_provider", "router"),
    ("app.api.seedance2_provider", "router"),
    ("app.api.kling_provider", "router"),
    ("app.api.runway_provider", "router"),
    ("app.api.volcengine_provider", "router"),
    ("app.drama.api", "ALL_DRAMA_ROUTERS"),
    ("app.render.manifest.api", "router"),
    ("app.video_engine.api.brain_routes", "router"),
}


class CriticalRouterImportError(RuntimeError):
    pass


ROUTER_SPECS: list[tuple[str, str]] = [
    ("app.api.storyboard_routes", "router"),
    ("app.storyboard_production.multi_angle_engine.router_patch", "router"),
    ("app.api.poster_video_render_routes", "router"),
    ("app.api.production_render_routes", "router"),
    ("app.api.smart_subtitle_routes", "router"),
    ("app.api.provider_payload_preview", "router"),
    ("app.api.audio", "router"),
    ("app.api.avatar_acting", "router"),
    ("app.api.avatar_analytics", "router"),
    ("app.api.avatar_builder", "router"),
    ("app.api.avatar_debug", "router"),
    ("app.api.avatar_embedding", "router"),
    ("app.api.avatar_governance", "router"),
    ("app.api.avatar_localization", "router"),
    ("app.api.avatar_marketplace", "router"),
    ("app.api.avatar_meta", "router"),
    ("app.api.avatar_tournament", "router"),
    ("app.api.provider_callbacks", "router"),
    ("app.api.render_dashboard", "router"),
    ("app.api.render_events", "router"),
    ("app.api.render_execution", "router"),
    ("app.api.render_job_health", "router"),
    ("app.api.render_job_status", "router"),
    ("app.api.render_quality", "router"),
    ("app.api.render_quality", "router_plural"),
    ("app.api.render_recovery", "router"),
    ("app.api.v1.provider_adapters", "router"),
    ("app.api.veo_workspace", "router"),
    ("app.api.video_router", "router"),
    ("app.api.seedance_provider", "router"),
    ("app.api.seedance2_provider", "router"),
    ("app.api.kling_provider", "router"),
    ("app.api.runway_provider", "router"),
    ("app.api.volcengine_provider", "router"),
    ("app.api.admin_circuit_breakers", "router"),
    ("app.api.admin_observability", "router"),
    ("app.drama.api", "ALL_DRAMA_ROUTERS"),
    ("app.render.manifest.api", "router"),
    ("app.video_engine.api.brain_routes", "router"),
    ("app.ads_engine.api.routes", "router"),
    ("app.api.code_intelligence", "router"),
    ("app.api.production_coordinator", "router"),
    ("app.api.trustgraph_runtime", "router"),
    ("app.api.cinematic_language", "router"),
]


def _is_feature_flag_enabled(env_var: str) -> bool:
    """Return True when a boolean feature-flag env var is set to a truthy value."""
    return os.getenv(env_var, "").strip().lower() in {"1", "true", "yes", "on"}


def _import_router(module_path: str, attr: str, *, critical: bool = False):
    try:
        module = importlib.import_module(module_path)
        obj = getattr(module, attr)
        if isinstance(obj, list):
            return [router for router in obj if router is not None]
        if obj is None:
            return []
        return [obj]
    except Exception as exc:  # noqa: BLE001
        _skipped_routers.append({"module": module_path, "attr": attr, "error": str(exc)})
        try:
            from app.core.production_gate import is_production_or_staging  # noqa: PLC0415
            in_production_like = is_production_or_staging()
        except Exception:
            in_production_like = False
        if in_production_like:
            log.error(
                "Router import failed in production — %s.%s: %s",
                module_path, attr, exc,
            )
            if critical:
                raise CriticalRouterImportError(
                    f"Critical router import failed: {module_path}.{attr}: {exc}"
                ) from exc
        else:
            log.warning("Skipping router %s.%s: %s", module_path, attr, exc)
        return []


def get_skipped_routers() -> list[dict[str, str]]:
    """Return information about routers that failed to import.

    Intended for startup health checks or a ``/health`` endpoint so operators
    can detect partial-registration failures without inspecting logs manually.
    Returns a snapshot of :data:`_skipped_routers`.
    """
    return list(_skipped_routers)


def register_all_routers(app: FastAPI) -> None:
    _skipped_routers.clear()
    router_specs = list(ROUTER_SPECS)
    if _is_feature_flag_enabled("ENABLE_AVATAR_COMMERCE_ROUTER"):
        router_specs.append(("app.api.avatar_commerce", "router"))
    for module_path, attr in router_specs:
        for router in _import_router(
            module_path,
            attr,
            critical=(module_path, attr) in _CRITICAL_ROUTERS,
        ):
            app.include_router(router)
