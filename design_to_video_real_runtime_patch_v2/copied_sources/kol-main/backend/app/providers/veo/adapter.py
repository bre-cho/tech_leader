from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any

from app.core.config import settings
from app.providers.base import BaseVideoProviderAdapter, ProviderAdapter
from app.providers.common import (
    ProviderAuthError,
    ProviderConfigError,
    ProviderHTTPError,
    ProviderTransientError,
    make_callback_event,
    mock_query_result,
    mock_submit_result,
    provider_mock_enabled,
    request_json,
)
from app.providers.config import env_bool, provider_default_dry_run
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)
from app.schemas.provider_schema import ProviderName, ProviderStatus

_logger = logging.getLogger(__name__)


class VeoAdapter(BaseVideoProviderAdapter):
    provider_name = "veo"

    
    @staticmethod
    def _build_idempotency_key(scene_payload: dict[str, Any]) -> str:
        basis = {
            "provider": "veo",
            "prompt": scene_payload.get("prompt") or scene_payload.get("visual_prompt") or scene_payload.get("description") or scene_payload.get("prompt_text"),
            "duration_seconds": scene_payload.get("duration_seconds", 8),
            "aspect_ratio": scene_payload.get("aspect_ratio", "16:9"),
            "scene_index": scene_payload.get("scene_index") or (scene_payload.get("metadata") or {}).get("scene_index"),
            "seed": scene_payload.get("seed"),
        }
        raw = json.dumps(basis, ensure_ascii=False, sort_keys=True, default=str)
        return "veo:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _base_url(self) -> str:
        if not settings.veo_api_base_url:
            raise ProviderConfigError("VEO_API_BASE_URL is required when Veo mock fallback is disabled")
        return settings.veo_api_base_url.rstrip("/")

    def _headers(self, *, idempotency_key: str | None = None) -> dict[str, str]:
        if not settings.veo_api_key:
            raise ProviderConfigError("VEO_API_KEY is required when Veo mock fallback is disabled")
        headers = {
            "Authorization": f"Bearer {settings.veo_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if idempotency_key:
            headers[settings.provider_idempotency_header] = idempotency_key
        return headers

    def _submit_url(self) -> str:
        return f"{self._base_url()}/{settings.veo_submit_path.lstrip('/')}"

    def _status_url(self, *, provider_task_id: str | None, provider_operation_name: str | None) -> str:
        ref = provider_operation_name or provider_task_id
        if not ref:
            raise ProviderConfigError("provider_operation_name or provider_task_id is required for Veo status query")
        template = settings.veo_status_path_template or "/v1/operations/{operation_name}"
        path = template.format(operation_name=ref, task_id=ref).lstrip("/")
        return f"{self._base_url()}/{path}"

    @staticmethod
    def _extract_video_url(payload: dict[str, Any]) -> str | None:
        candidates = [
            payload.get("output_video_url"),
            payload.get("video_url"),
            payload.get("uri"),
            payload.get("url"),
        ]
        response = payload.get("response") if isinstance(payload.get("response"), dict) else {}
        result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        output = payload.get("output") if isinstance(payload.get("output"), dict) else {}
        video = output.get("video") if isinstance(output.get("video"), dict) else {}
        candidates.extend([
            response.get("output_video_url"),
            response.get("video_url"),
            result.get("output_video_url"),
            result.get("video_url"),
            output.get("output_video_url"),
            output.get("video_url"),
            video.get("url"),
            video.get("uri"),
        ])
        for value in candidates:
            if value:
                return str(value)
        return None

    @staticmethod
    def _normalize_state(payload: dict[str, Any]) -> tuple[str, str | None]:
        raw = str(
            payload.get("state")
            or payload.get("status")
            or payload.get("done")
            or payload.get("provider_status")
            or "processing"
        )
        lowered = raw.strip().lower()
        if lowered in {"true", "done", "success", "succeeded", "completed", "complete"}:
            return "succeeded", raw
        if lowered in {"false", "queued", "pending", "running", "processing", "submitted", "in_progress"}:
            return "processing", raw
        if lowered in {"failed", "error", "errored", "cancelled", "canceled"}:
            return ("canceled" if "cancel" in lowered else "failed"), raw
        if isinstance(payload.get("error"), (dict, str)):
            return "failed", raw
        if payload.get("done") is True:
            return "succeeded", raw
        # Unrecognised state — log a warning so ops can update the state map.
        _logger.warning(
            "VeoAdapter._normalize_state: unrecognised provider state %r in payload keys=%s; "
            "mapping to 'processing'. Update _normalize_state if this is a terminal state.",
            raw,
            sorted(payload.keys()),
        )
        return "processing", raw

    async def submit(
        self,
        scene_payload: dict,
        callback_url: str | None,
    ) -> NormalizedSubmitResult:
        model = scene_payload.get("provider_model") or settings.veo_default_model
        idempotency_key = scene_payload.get("idempotency_key") or self._build_idempotency_key(scene_payload)
        if provider_mock_enabled():
            return mock_submit_result(
                provider=self.provider_name,
                model=model,
                callback_url=callback_url,
                use_operation=True,
                reason="mock_veo_submit",
            )

        body = {
            "model": model,
            "prompt": scene_payload.get("prompt") or scene_payload.get("visual_prompt") or scene_payload.get("description"),
            "duration_seconds": scene_payload.get("duration_seconds", 8),
            "aspect_ratio": scene_payload.get("aspect_ratio", "16:9"),
            "style": scene_payload.get("style") or scene_payload.get("style_preset") or "cinematic",
            "negative_prompt": scene_payload.get("negative_prompt", ""),
            "callback_url": callback_url,
            "metadata": {
                "idempotency_key": idempotency_key,
                "scene_index": scene_payload.get("scene_index"),
                "title": scene_payload.get("title"),
            },
        }
        body = {key: value for key, value in body.items() if value is not None}

        try:
            started = time.perf_counter()
            payload = await request_json(
                method="POST",
                url=self._submit_url(),
                headers=self._headers(idempotency_key=idempotency_key),
                json_body=body,
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
        except (ProviderConfigError, ProviderAuthError, ProviderHTTPError, ProviderTransientError) as exc:
            return NormalizedSubmitResult(
                accepted=False,
                provider=self.provider_name,
                provider_model=model,
                callback_url_used=callback_url,
                error_message=str(exc),
                raw_response={"error": str(exc)},
                idempotency_key=idempotency_key,
            )

        provider_task_id = payload.get("id") or payload.get("task_id") or payload.get("job_id")
        provider_operation_name = payload.get("name") or payload.get("operation_name") or payload.get("operation")
        accepted = bool(provider_task_id or provider_operation_name or payload.get("accepted", True))
        return NormalizedSubmitResult(
            accepted=accepted,
            provider=self.provider_name,
            provider_model=model,
            provider_request_id=str(payload.get("request_id")) if payload.get("request_id") else None,
            provider_task_id=str(provider_task_id) if provider_task_id else None,
            provider_operation_name=str(provider_operation_name) if provider_operation_name else None,
            provider_status_raw=str(payload.get("status") or payload.get("state") or "SUBMITTED"),
            idempotency_key=idempotency_key,
            latency_ms=latency_ms,
            callback_url_used=callback_url,
            raw_response=payload,
            error_message=None if accepted else str(payload.get("error") or "Veo submit rejected"),
        )

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        if provider_mock_enabled():
            return mock_query_result(self.provider_name)

        try:
            started = time.perf_counter()
            payload = await request_json(
                method="GET",
                url=self._status_url(
                    provider_task_id=provider_task_id,
                    provider_operation_name=provider_operation_name,
                ),
                headers=self._headers(),
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
        except (ProviderConfigError, ProviderAuthError, ProviderHTTPError, ProviderTransientError) as exc:
            return NormalizedStatusResult(
                provider=self.provider_name,
                state="failed",
                error_message=str(exc),
                failure_code="VEO_QUERY_FAILED",
                failure_category="provider_query",
                raw_response={"error": str(exc)},
                retry_after_seconds=None,
            )

        state, raw_status = self._normalize_state(payload)
        error_obj = payload.get("error")
        error_message = None
        if isinstance(error_obj, dict):
            error_message = error_obj.get("message") or json.dumps(error_obj, ensure_ascii=False)
        elif error_obj:
            error_message = str(error_obj)

        return NormalizedStatusResult(
            provider=self.provider_name,
            state=state,
            provider_status_raw=raw_status,
            output_video_url=self._extract_video_url(payload),
            output_thumbnail_url=payload.get("output_thumbnail_url") or payload.get("thumbnail_url"),
            metadata={"provider_task_id": provider_task_id, "provider_operation_name": provider_operation_name},
            error_message=error_message,
            failure_code="VEO_PROVIDER_ERROR" if state == "failed" else None,
            failure_category="provider" if state == "failed" else None,
            raw_response=payload,
            latency_ms=latency_ms,
        )

    def verify_callback(
        self,
        headers: dict[str, str],
        raw_body: bytes,
    ) -> bool:
        secret = os.getenv("VEO_CALLBACK_SECRET", "")
        if not secret:
            return not bool(settings.provider_callback_strict_signature)

        provided = (headers.get("x-render-signature") or "").removeprefix("sha256=").strip()
        expected = hashlib.sha256(secret.encode("utf-8") + raw_body).hexdigest()
        return provided == expected

    def normalize_callback(
        self,
        headers: dict[str, str],
        payload: dict,
    ) -> NormalizedCallbackEvent:
        provider_task_id = payload.get("provider_task_id") or payload.get("task_id") or payload.get("id")
        provider_operation_name = payload.get("provider_operation_name") or payload.get("operation_name") or payload.get("name")
        status_raw = str(payload.get("status") or payload.get("state") or payload.get("done") or "processing")
        state, _ = self._normalize_state(payload)

        idem_source = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        event_idempotency_key = str(payload.get("event_id") or hashlib.sha256(idem_source.encode("utf-8")).hexdigest())

        return make_callback_event(
            provider=self.provider_name,
            payload=payload,
            event_idempotency_key=event_idempotency_key,
            event_type=str(payload.get("event_type") or "provider_callback"),
            provider_task_id=provider_task_id,
            provider_operation_name=provider_operation_name,
            provider_status_raw=status_raw,
            state=state,
            output_video_url=payload.get("output_video_url") or self._extract_video_url(payload),
            output_thumbnail_url=payload.get("output_thumbnail_url") or payload.get("thumbnail_url"),
            error_message=payload.get("error_message"),
            failure_code=payload.get("failure_code"),
            failure_category=payload.get("failure_category"),
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
        )


class VeoProviderAdapter(ProviderAdapter):
    provider_name = ProviderName.veo

    def status(self) -> ProviderStatus:
        configured = bool(os.getenv("VEO_API_KEY") and os.getenv("VEO_API_BASE_URL"))
        enabled = env_bool("VEO_PROVIDER_ENABLED", False)

        return ProviderStatus(
            provider=self.provider_name,
            enabled=enabled,
            configured=configured,
            dry_run_default=provider_default_dry_run(),
            message="Veo provider ready for real submit/query transport."
            if configured
            else "Veo API config is missing.",
        )

    def build_payload(self, operation: str, input_data: dict[str, Any]) -> dict[str, Any]:
        if operation == "generate_video":
            return {
                "operation": operation,
                "prompt": input_data.get("prompt"),
                "duration_seconds": input_data.get("duration_seconds", 8),
                "aspect_ratio": input_data.get("aspect_ratio", "16:9"),
                "style": input_data.get("style", "cinematic"),
                "negative_prompt": input_data.get("negative_prompt", ""),
                "callback_url": input_data.get("callback_url"),
            }

        if operation == "get_job_status":
            return {
                "operation": operation,
                "external_job_id": input_data.get("external_job_id"),
            }

        return {"operation": operation, "input": input_data}
