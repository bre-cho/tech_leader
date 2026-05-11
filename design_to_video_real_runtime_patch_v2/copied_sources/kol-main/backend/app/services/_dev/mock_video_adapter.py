"""Dev-only mock video provider adapter.

.. warning::
    This adapter MUST NOT be used in production or staging environments.
    ``get_provider_adapter("mock")`` raises ``ValueError`` when
    ``is_production_or_staging()`` is True — this is enforced at both the
    adapter factory level and at startup via ``_check_failover_order_or_raise()``.

    This module lives in ``services/_dev/`` to make its dev-only nature
    explicit and to keep production modules clean.
"""
from __future__ import annotations

import time

from app.providers.base import BaseVideoProviderAdapter
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)


class MockVideoAdapter(BaseVideoProviderAdapter):
    """Local/CI mock adapter — always succeeds, never touches a real provider.

    Gated by ``ALLOW_MOCK_PROVIDER_RESPONSE`` env var for ``query()`` and by
    ``is_production_or_staging()`` at the factory level for all methods.
    """

    provider_name = "mock"

    async def submit(self, scene_payload: dict, callback_url: str | None) -> NormalizedSubmitResult:
        suffix = str(int(time.time() * 1000))
        return NormalizedSubmitResult(
            accepted=True,
            provider=self.provider_name,
            provider_model=scene_payload.get("provider_model") or "mock-video",
            provider_task_id=f"mock-task-{suffix}",
            provider_operation_name="mock_submit",
            provider_status_raw="MOCK_SUBMITTED",
            callback_url_used=callback_url,
            raw_response={"mock": True},
        )

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        from app.core.production_gate import ensure_stub_allowed  # noqa: PLC0415
        from app.services.fake_success_guard import assert_no_fake_success_payload  # noqa: PLC0415

        ensure_stub_allowed(
            "video mock response",
            allow_env="ALLOW_MOCK_PROVIDER_RESPONSE",
        )
        payload = {
            "provider": self.provider_name,
            "state": "succeeded",
            "provider_status_raw": "MOCK_SUCCEEDED",
            "output_video_url": f"https://example.invalid/mock-output/{provider_task_id or 'video'}.mp4",
            "raw_response": {
                "mock": True,
                "provider_task_id": provider_task_id,
                "operation": provider_operation_name,
            },
        }
        assert_no_fake_success_payload(payload, context="mock_video_adapter:query")
        return NormalizedStatusResult(**payload)

    def verify_callback(self, headers: dict[str, str], raw_body: bytes) -> bool:
        return True

    def normalize_callback(self, headers: dict[str, str], payload: dict) -> NormalizedCallbackEvent:
        return NormalizedCallbackEvent(
            provider=self.provider_name,
            event_type="mock_callback",
            event_idempotency_key=str(payload.get("event_id") or f"mock:{hash(str(payload))}"),
            provider_task_id=str(payload.get("task_id") or "") or None,
            state="succeeded",
            output_video_url=payload.get("output_video_url"),
            raw_payload=payload,
        )
