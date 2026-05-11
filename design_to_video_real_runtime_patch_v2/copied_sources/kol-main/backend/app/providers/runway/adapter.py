from __future__ import annotations

import hashlib
import json
from typing import Any

from app.core.config import settings
from app.providers.base import BaseVideoProviderAdapter
from app.providers.common import (
    ProviderConfigError,
    make_callback_event,
    mock_query_result,
    mock_submit_result,
    provider_mock_enabled,
    request_json,
    verify_hmac_signature,
)
from app.providers.runway.auth import runway_headers
from app.providers.runway.payload_builder import build_runway_body, runway_mode
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)


class RunwayAdapter(BaseVideoProviderAdapter):
    """
    RUNWAY OFFICIAL API PATCH V2

    Officialized Runway adapter for Visual Engine V4.

    Auth:
      RUNWAYML_API_SECRET -> Authorization: Bearer <secret>

    Modes:
      text_to_video:
        POST /v1/image_to_video with promptImage omitted for Gen-4.5 text-to-video

      image_to_video:
        POST /v1/image_to_video with promptImage

      video_to_video:
        POST /v1/video_to_video when your account/model supports it

    Notes:
      - Runway SDKs have built-in polling.
      - This adapter provides REST-compatible normalized submit/query contract.
    """

    provider_name = "runway"

    def _base_url(self) -> str:
        return getattr(settings, "runway_base_url", "https://api.dev.runwayml.com").rstrip("/")

    def _submit_url(self, mode: str) -> str:
        base = self._base_url()
        if mode in {"text_to_video", "image_to_video"}:
            return f"{base}/v1/image_to_video"
        if mode == "video_to_video":
            return f"{base}/v1/video_to_video"
        raise ProviderConfigError(f"Unsupported Runway mode: {mode}")

    def _query_url(self, task_id: str) -> str:
        return f"{self._base_url()}/v1/tasks/{task_id}"

    def _extract_task_id(self, raw: dict[str, Any]) -> str | None:
        candidates = [
            raw.get("id"),
            raw.get("task_id"),
            raw.get("uuid"),
            raw.get("taskId"),
        ]
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        candidates.extend([data.get("id"), data.get("task_id"), data.get("taskId")])
        for value in candidates:
            if value:
                return str(value)
        return None

    def _extract_status_raw(self, raw: dict[str, Any]) -> str:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        return str(
            raw.get("status")
            or raw.get("state")
            or data.get("status")
            or data.get("state")
            or ""
        ).lower()

    def _normalize_state(self, status_raw: str) -> str:
        if status_raw in {"succeeded", "success", "completed", "complete"}:
            return "succeeded"
        if status_raw in {"failed", "error"}:
            return "failed"
        if status_raw in {"cancelled", "canceled"}:
            return "canceled"
        return "processing"

    def _extract_output_url(self, raw: dict[str, Any]) -> str | None:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else raw
        output = data.get("output") or data.get("outputs") or data.get("result") or raw.get("output")

        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get("url") or first.get("uri") or first.get("video_url")

        if isinstance(output, dict):
            return output.get("url") or output.get("uri") or output.get("video_url")

        if isinstance(output, str):
            return output

        return (
            data.get("output_url")
            or data.get("video_url")
            or data.get("url")
            or raw.get("output_url")
            or raw.get("video_url")
            or raw.get("url")
        )

    def _extract_error(self, raw: dict[str, Any]) -> str | None:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        message = (
            raw.get("error")
            or raw.get("message")
            or data.get("error")
            or data.get("message")
            or data.get("failure")
        )
        if message:
            return str(message)
        return None

    async def submit(self, scene_payload: dict[str, Any], callback_url: str | None) -> NormalizedSubmitResult:
        if provider_mock_enabled():
            return mock_submit_result(
                provider=self.provider_name,
                model=scene_payload.get("provider_model") or getattr(settings, "runway_default_model", "gen4.5"),
                callback_url=callback_url,
                reason="mock_runway_submit",
            )

        mode = runway_mode(scene_payload)
        body = build_runway_body(scene_payload)

        if callback_url:
            body["webhook"] = callback_url

        raw = await request_json(
            method="POST",
            url=self._submit_url(mode),
            headers=runway_headers(),
            json_body=body,
        )

        task_id = self._extract_task_id(raw)
        status_raw = self._extract_status_raw(raw) or "submitted"

        return NormalizedSubmitResult(
            accepted=bool(task_id),
            provider=self.provider_name,
            provider_model=body.get("model"),
            provider_task_id=task_id,
            provider_operation_name=mode,
            provider_status_raw=status_raw,
            callback_url_used=callback_url,
            raw_response=raw,
            error_message=None if task_id else (self._extract_error(raw) or "Runway did not return task id"),
        )

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        if provider_mock_enabled():
            return mock_query_result(self.provider_name)

        if not provider_task_id:
            raise ProviderConfigError("Runway query requires provider_task_id")

        raw = await request_json(
            method="GET",
            url=self._query_url(provider_task_id),
            headers=runway_headers(),
        )

        status_raw = self._extract_status_raw(raw)
        state = self._normalize_state(status_raw)

        return NormalizedStatusResult(
            provider=self.provider_name,
            state=state,
            provider_status_raw=status_raw,
            output_video_url=self._extract_output_url(raw),
            raw_response=raw,
            error_message=self._extract_error(raw) if state == "failed" else None,
        )

    def verify_callback(self, headers: dict[str, str], raw_body: bytes) -> bool:
        return verify_hmac_signature(
            headers=headers,
            raw_body=raw_body,
            secret=settings.provider_callback_shared_secret,
        )

    def normalize_callback(self, headers: dict[str, str], payload: dict) -> NormalizedCallbackEvent:
        status_raw = self._extract_status_raw(payload)
        idem_source = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        event_idempotency_key = str(
            payload.get("event_id")
            or payload.get("id")
            or payload.get("taskId")
            or hashlib.sha256(idem_source.encode("utf-8")).hexdigest()
        )
        return make_callback_event(
            provider=self.provider_name,
            payload=payload,
            event_idempotency_key=event_idempotency_key,
            event_type=str(payload.get("type") or "provider_callback"),
            provider_task_id=str(payload.get("taskId") or payload.get("task_id") or "") or None,
            provider_status_raw=status_raw or None,
            state=self._normalize_state(status_raw),
            output_video_url=self._extract_output_url(payload),
            error_message=self._extract_error(payload),
        )
