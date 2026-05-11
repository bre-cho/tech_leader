from __future__ import annotations

import logging
import os
import threading

from app.core.production_gate import ensure_stub_allowed
from app.providers.base import BaseVideoProviderAdapter
from app.providers.common import (
    ProviderAuthError,
    ProviderConfigError,
    ProviderHTTPError,
    ProviderTransientError,
)
from app.providers.kling.adapter import KlingAdapter
from app.providers.runway.adapter import RunwayAdapter
from app.providers.seedance.adapter import SeedanceAdapter
from app.providers.seedance2.adapter import Seedance2Adapter
from app.providers.veo.adapter import VeoAdapter
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)
from app.services.fake_success_guard import assert_no_fake_success_payload
from app.services.provider_normalize import normalize_provider_name
from app.services.provider_routing.circuit_breaker import CircuitOpenError, get_breaker


_ADAPTER_CACHE: dict[str, BaseVideoProviderAdapter] = {}
_ADAPTER_CACHE_LOCK = threading.Lock()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Failover registry
# ---------------------------------------------------------------------------
# Ordered list of provider keys tried in sequence when the primary provider
# fails with a quota/transient error on submit. The first key is always the
# one requested by the caller; subsequent entries are fallbacks.
#
# The default covers the three most capable production providers so a single
# provider outage does not immediately surface to the user.  The order matches
# the "cinematic_ads" routing profile (highest quality first).
#
# Set VIDEO_PROVIDER_FAILOVER_ORDER=veo,simulated (comma-separated) to
# override. An empty value disables failover (only the primary is tried).
# ---------------------------------------------------------------------------
_DEFAULT_FAILOVER_ORDER: list[str] = ["veo", "seedance", "runway"]


def _failover_order() -> list[str]:
    raw = os.environ.get("VIDEO_PROVIDER_FAILOVER_ORDER", "").strip()
    if raw:
        return [p.strip() for p in raw.split(",") if p.strip()]
    return list(_DEFAULT_FAILOVER_ORDER)


class MockVideoAdapter(BaseVideoProviderAdapter):
    """Backward-compat shim: delegates to the dev-only mock adapter.

    This class is kept here solely so that existing ``isinstance`` checks and
    test imports are not broken.  New code should import directly from
    ``app.services._dev.mock_video_adapter``.

    The adapter is gated by ``is_production_or_staging()`` inside
    ``get_provider_adapter()``; it is never instantiated in prod/staging.
    """

    provider_name = "mock"

    def __init__(self) -> None:
        from app.services._dev.mock_video_adapter import MockVideoAdapter as _Real  # noqa: PLC0415
        self._impl = _Real()

    async def submit(self, scene_payload: dict, callback_url: str | None) -> NormalizedSubmitResult:
        return await self._impl.submit(scene_payload, callback_url)

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        return await self._impl.query(
            provider_task_id=provider_task_id,
            provider_operation_name=provider_operation_name,
        )

    def verify_callback(self, headers: dict[str, str], raw_body: bytes) -> bool:
        return self._impl.verify_callback(headers, raw_body)

    def normalize_callback(self, headers: dict[str, str], payload: dict) -> NormalizedCallbackEvent:
        return self._impl.normalize_callback(headers, payload)


def get_provider_adapter(provider: str) -> BaseVideoProviderAdapter:
    provider_key = normalize_provider_name(provider)

    with _ADAPTER_CACHE_LOCK:
        if provider_key in _ADAPTER_CACHE:
            return _ADAPTER_CACHE[provider_key]

        if provider_key == "veo":
            adapter: BaseVideoProviderAdapter = VeoAdapter()
        elif provider_key == "runway":
            adapter = RunwayAdapter()
        elif provider_key == "kling":
            adapter = KlingAdapter()
        elif provider_key == "seedance":
            adapter = SeedanceAdapter()
        elif provider_key == "seedance2":
            adapter = Seedance2Adapter()
        elif provider_key == "mock":
            from app.core.production_gate import is_production_or_staging  # noqa: PLC0415
            if is_production_or_staging():
                raise ValueError(
                    "mock provider is disabled in production/staging. "
                    "Remove 'mock' from VIDEO_PROVIDER_FAILOVER_ORDER and use a real provider."
                )
            adapter = MockVideoAdapter()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        _ADAPTER_CACHE[provider_key] = adapter
        return adapter


def invalidate_adapter_cache(provider: str | None = None) -> None:
    """Remove cached adapter(s) so they are re-instantiated on next use.

    Pass *provider* to evict a specific provider (e.g. after credential rotation).
    Pass ``None`` to flush the entire cache.
    """
    with _ADAPTER_CACHE_LOCK:
        if provider is None:
            _ADAPTER_CACHE.clear()
        else:
            provider_key = normalize_provider_name(provider)
            _ADAPTER_CACHE.pop(provider_key, None)


async def submit_render_task(
    *,
    provider: str,
    scene_payload: dict,
    callback_url: str | None,
) -> NormalizedSubmitResult:
    normalized_provider = normalize_provider_name(provider)

    order = [normalized_provider] + [p for p in _failover_order() if p != normalized_provider]

    last_result: NormalizedSubmitResult | None = None
    for attempt_provider in order:
        breaker = get_breaker(attempt_provider)
        if breaker.is_open():
            logger.warning(
                "provider_submit_circuit_open: provider=%s circuit is OPEN; skipping to next in failover order",
                attempt_provider,
            )
            last_result = NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=None,
                error_message="Circuit breaker OPEN",
            )
            continue
        try:
            adapter = get_provider_adapter(attempt_provider)
            result = await adapter.submit(
                scene_payload=scene_payload,
                callback_url=callback_url,
            )
            if result.accepted:
                breaker.record_success()
                if attempt_provider != normalized_provider:
                    logger.warning(
                        "provider_submit_failover: primary=%s failed, used fallback=%s",
                        normalized_provider,
                        attempt_provider,
                    )
                return NormalizedSubmitResult(
                    accepted=result.accepted,
                    provider=result.provider or attempt_provider,
                    provider_model=result.provider_model,
                    provider_request_id=result.provider_request_id,
                    provider_task_id=result.provider_task_id,
                    provider_operation_name=result.provider_operation_name,
                    provider_status_raw=result.provider_status_raw,
                    idempotency_key=result.idempotency_key,
                    latency_ms=result.latency_ms,
                    retry_after_seconds=result.retry_after_seconds,
                    callback_url_used=result.callback_url_used or callback_url,
                    raw_response=result.raw_response,
                    error_message=result.error_message,
                )

            logger.warning(
                "provider_submit_not_accepted: provider=%s error=%s; trying next in failover order",
                attempt_provider,
                result.error_message,
            )
            breaker.record_failure()
            last_result = NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=result.raw_response,
                error_message=result.error_message,
            )
        except ProviderConfigError as exc:
            logger.error(
                "provider_submit_config_error",
                extra={"provider": attempt_provider, "error_type": type(exc).__name__, "error": str(exc)},
            )
            last_result = NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=None,
                error_message=str(exc),
            )
        except ProviderAuthError as exc:
            logger.error(
                "provider_submit_auth_error",
                extra={"provider": attempt_provider, "error_type": type(exc).__name__, "error": str(exc)},
            )
            return NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=None,
                error_message=str(exc),
            )
        except (ProviderTransientError, ProviderHTTPError, ValueError) as exc:
            logger.warning(
                "provider_submit_error: provider=%s error=%s; trying next in failover order",
                attempt_provider,
                exc,
            )
            breaker.record_failure()
            last_result = NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=None,
                error_message=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "provider_submit_unhandled_error",
                extra={"provider": attempt_provider, "error_type": type(exc).__name__, "error": str(exc)},
            )
            breaker.record_failure()
            last_result = NormalizedSubmitResult(
                accepted=False,
                provider=attempt_provider,
                provider_model=scene_payload.get("provider_model"),
                callback_url_used=callback_url,
                raw_response=None,
                error_message=str(exc),
            )

    return last_result or NormalizedSubmitResult(
        accepted=False,
        provider=normalized_provider,
        provider_model=scene_payload.get("provider_model"),
        callback_url_used=callback_url,
        raw_response=None,
        error_message="All providers in failover chain failed",
    )


async def query_render_task(
    *,
    provider: str,
    provider_task_id: str | None,
    provider_operation_name: str | None,
) -> NormalizedStatusResult:
    normalized_provider = normalize_provider_name(provider)
    breaker = get_breaker(normalized_provider)

    if breaker.is_open():
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message="Circuit breaker is open for provider query.",
            failure_code="CIRCUIT_BREAKER_OPEN",
            failure_category="provider_circuit_open",
            raw_response=None,
        )

    try:
        adapter = get_provider_adapter(normalized_provider)
        result = await adapter.query(
            provider_task_id=provider_task_id,
            provider_operation_name=provider_operation_name,
        )

        return NormalizedStatusResult(
            provider=result.provider or normalized_provider,
            state=result.state,
            provider_status_raw=result.provider_status_raw,
            output_video_url=result.output_video_url,
            output_thumbnail_url=result.output_thumbnail_url,
            metadata=result.metadata,
            error_message=result.error_message,
            failure_code=result.failure_code,
            failure_category=result.failure_category,
            raw_response=result.raw_response,
            latency_ms=result.latency_ms,
            retry_after_seconds=result.retry_after_seconds,
        )
    except ProviderConfigError as exc:
        logger.error(
            "provider_query_config_error",
            extra={"provider": normalized_provider, "error_type": type(exc).__name__, "error": str(exc)},
        )
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message=str(exc),
            failure_code="PROVIDER_CONFIG_ERROR",
            failure_category="provider_config",
            raw_response=None,
        )
    except ProviderAuthError as exc:
        logger.error(
            "provider_query_auth_error",
            extra={"provider": normalized_provider, "error_type": type(exc).__name__, "error": str(exc)},
        )
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message=str(exc),
            failure_code="PROVIDER_AUTH_ERROR",
            failure_category="provider_auth",
            raw_response=None,
        )
    except ProviderTransientError as exc:
        breaker.record_failure()
        logger.warning(
            "provider_query_transient_error",
            extra={"provider": normalized_provider, "error_type": type(exc).__name__, "error": str(exc)},
        )
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message=str(exc),
            failure_code="PROVIDER_TRANSIENT_ERROR",
            failure_category="provider_poll_transient",
            raw_response=None,
        )
    except (ProviderHTTPError, ValueError) as exc:
        logger.error(
            "provider_query_error",
            extra={"provider": normalized_provider, "error_type": type(exc).__name__, "error": str(exc)},
        )
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message=str(exc),
            failure_code="PROVIDER_POLL_ERROR",
            failure_category="provider_poll",
            raw_response=None,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "provider_query_unhandled_error",
            extra={"provider": normalized_provider, "error_type": type(exc).__name__, "error": str(exc)},
        )
        return NormalizedStatusResult(
            provider=normalized_provider,
            state="failed",
            provider_status_raw=None,
            output_video_url=None,
            output_thumbnail_url=None,
            metadata=None,
            error_message=str(exc),
            failure_code="PROVIDER_ROUTER_QUERY_EXCEPTION",
            failure_category="provider_poll",
            raw_response=None,
        )


def verify_render_callback(
    *,
    provider: str,
    headers: dict[str, str],
    raw_body: bytes,
) -> bool:
    normalized_provider = normalize_provider_name(provider)

    try:
        adapter = get_provider_adapter(normalized_provider)
        return bool(adapter.verify_callback(headers, raw_body))
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "provider_callback_verify_error",
            extra={
                "provider": normalized_provider,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "header_keys": sorted(headers.keys()),
            },
        )
        return False


def normalize_render_callback(
    *,
    provider: str,
    headers: dict[str, str],
    payload: dict,
) -> NormalizedCallbackEvent:
    normalized_provider = normalize_provider_name(provider)

    adapter = get_provider_adapter(normalized_provider)
    result = adapter.normalize_callback(headers, payload)

    return NormalizedCallbackEvent(
        provider=result.provider or normalized_provider,
        event_type=result.event_type,
        event_idempotency_key=result.event_idempotency_key,
        provider_task_id=result.provider_task_id,
        provider_operation_name=result.provider_operation_name,
        provider_status_raw=result.provider_status_raw,
        state=result.state,
        output_video_url=result.output_video_url,
        output_thumbnail_url=result.output_thumbnail_url,
        metadata=result.metadata,
        error_message=result.error_message,
        failure_code=result.failure_code,
        failure_category=result.failure_category,
        raw_payload=result.raw_payload,
    )
