from __future__ import annotations

import json
import os
from typing import Any, Protocol

from app.core.production_gate import is_production_or_staging
from app.core.config import settings
from app.providers.common import provider_mock_enabled
from app.services.provider_router import query_render_task, submit_render_task


class ProviderClientProtocol(Protocol):
    async def dispatch_scene(self, *, job: Any, scene_task: Any) -> dict[str, Any]:
        ...

    async def poll_scene(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
        scene_task: Any,
        job: Any,
    ) -> dict[str, Any]:
        ...


class MockProviderClient:
    """
    Mock production-safe client để pipeline chạy kín local/dev.
    Có thể thay bằng VeoProviderClient thật sau.
    """

    async def dispatch_scene(self, *, job: Any, scene_task: Any) -> dict[str, Any]:
        return {
            "status": "submitted",
            "provider_task_id": f"mock-task-{scene_task.id}",
            "provider_operation_name": f"mock-op-{scene_task.id}",
            "provider_payload": {
                "provider": getattr(job, "provider", "mock"),
                "scene_index": getattr(scene_task, "scene_index", None),
            },
        }

    async def poll_scene(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
        scene_task: Any,
        job: Any,
    ) -> dict[str, Any]:
        output_path = getattr(scene_task, "mock_output_path", None) or getattr(scene_task, "output_path", None)

        return {
            "status": "succeeded",
            "provider_task_id": provider_task_id,
            "provider_operation_name": provider_operation_name,
            "output_url": None,
            "output_path": output_path,
            "provider_payload": {
                "provider": getattr(job, "provider", "mock"),
                "provider_task_id": provider_task_id,
                "provider_operation_name": provider_operation_name,
            },
            "error_message": None,
        }


class ProviderRouterClient:
    """Provider client shim that routes submit/query calls through provider_router."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    async def dispatch_scene(self, *, job: Any, scene_task: Any) -> dict[str, Any]:
        payload_raw = getattr(scene_task, "request_payload_json", None)
        if isinstance(payload_raw, dict):
            payload = payload_raw
        else:
            try:
                payload = json.loads(payload_raw or "{}")
            except (TypeError, ValueError):
                payload = {}

        result = await submit_render_task(
            provider=self.provider_name,
            scene_payload=payload,
            callback_url=None,
        )
        return {
            "status": "submitted" if result.accepted else "failed",
            "provider_task_id": result.provider_task_id,
            "provider_operation_name": result.provider_operation_name,
            "provider_payload": result.raw_response,
            "error_message": result.error_message,
        }

    async def poll_scene(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
        scene_task: Any,
        job: Any,
    ) -> dict[str, Any]:
        result = await query_render_task(
            provider=self.provider_name,
            provider_task_id=provider_task_id,
            provider_operation_name=provider_operation_name,
        )
        return {
            "status": result.state,
            "provider_task_id": provider_task_id,
            "provider_operation_name": provider_operation_name,
            "output_url": result.output_video_url,
            "output_path": getattr(scene_task, "output_path", None),
            "provider_payload": result.raw_response,
            "error_message": result.error_message,
            "failure_code": result.failure_code,
            "failure_category": result.failure_category,
        }


def _legacy_mock_client_enabled() -> bool:
    return os.getenv("PROVIDER_FACTORY_ENABLE_LEGACY_MOCK_CLIENT", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_provider_client(provider_name: str) -> ProviderClientProtocol:
    normalized = str(provider_name or "").strip().lower()

    # All real providers route through ProviderRouterClient which delegates to
    # provider_router.submit_render_task / query_render_task.  This covers veo,
    # runway, kling, seedance, and seedance2 uniformly.
    _REAL_PROVIDERS = {
        "veo", "veo_3", "veo_3_1",
        "runway",
        "kling",
        "seedance",
        "seedance2",
    }
    if normalized in _REAL_PROVIDERS:
        # Normalise aliases to the canonical provider key expected by provider_router.
        canonical = normalized if normalized not in {"veo_3", "veo_3_1"} else "veo"
        return ProviderRouterClient(canonical)

    if is_production_or_staging():
        raise ValueError(
            f"Unsupported provider: {provider_name}; "
            "legacy MockProviderClient is disabled in production/staging. "
            "Use a canonical provider route through app.services.provider_router."
        )

    if provider_mock_enabled() and _legacy_mock_client_enabled():
        return MockProviderClient()
    if provider_mock_enabled() and not _legacy_mock_client_enabled():
        raise ValueError(
            f"Unsupported provider: {provider_name}; "
            "legacy MockProviderClient is disabled by default. "
            "Set PROVIDER_FACTORY_ENABLE_LEGACY_MOCK_CLIENT=true only for local/dev migration scenarios."
        )
    raise ValueError(
        f"Unsupported provider: {provider_name}; "
        f"mock fallback is disabled for environment '{settings.app_env}' "
        "(set PROVIDER_ALLOW_MOCK_FALLBACK=true in non-production environments to enable)."
    )
