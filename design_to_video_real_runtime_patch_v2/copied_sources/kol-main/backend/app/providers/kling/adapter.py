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
from app.providers.kling.auth import generate_kling_jwt
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)


class KlingAdapter(BaseVideoProviderAdapter):
    """
    KLING OFFICIAL API PATCH V2

    Officialized Kling adapter for Visual Engine V4.

    Auth:
      KLING_ACCESS_KEY + KLING_SECRET_KEY -> JWT -> Authorization Bearer token

    Modes:
      text_to_video:
        POST /v1/videos/text2video
        GET  /v1/videos/text2video/{task_id}

      image_to_video:
        POST /v1/videos/image2video
        GET  /v1/videos/image2video/{task_id}

    Normalized input payload:
      - video_prompt | prompt | text
      - negative_prompt
      - aspect_ratio
      - duration_seconds
      - provider_model
      - start_image_url | image_url
      - callback_url
      - camera_control
      - cfg_scale
    """

    provider_name = "kling"

    def _headers(self) -> dict[str, str]:
        token = generate_kling_jwt()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _base_url(self) -> str:
        return getattr(settings, "kling_base_url", "https://api.klingai.com").rstrip("/")

    def _mode(self, scene_payload: dict[str, Any]) -> str:
        if scene_payload.get("start_image_url") or scene_payload.get("image_url"):
            return "image_to_video"
        return "text_to_video"

    def _submit_url(self, mode: str) -> str:
        if mode == "image_to_video":
            return f"{self._base_url()}/v1/videos/image2video"
        return f"{self._base_url()}/v1/videos/text2video"

    def _query_url(self, mode: str, task_id: str) -> str:
        if mode == "image_to_video":
            return f"{self._base_url()}/v1/videos/image2video/{task_id}"
        return f"{self._base_url()}/v1/videos/text2video/{task_id}"

    def _prompt(self, scene_payload: dict[str, Any]) -> str:
        return (
            scene_payload.get("video_prompt")
            or scene_payload.get("prompt")
            or scene_payload.get("text")
            or ""
        )

    def _build_body(self, scene_payload: dict[str, Any]) -> dict[str, Any]:
        mode = self._mode(scene_payload)

        prompt = self._prompt(scene_payload)
        if not prompt:
            raise ProviderConfigError("Kling render requires prompt/video_prompt/text")

        body: dict[str, Any] = {
            "model_name": scene_payload.get("provider_model")
            or getattr(settings, "kling_default_model", "kling-v2-1"),
            "prompt": prompt,
            "negative_prompt": scene_payload.get("negative_prompt")
            or "random face, inconsistent character, bad hands, blurry, distorted, watermark, extra text",
            "cfg_scale": scene_payload.get("cfg_scale", getattr(settings, "kling_default_cfg_scale", 0.5)),
        }

        aspect_ratio = scene_payload.get("aspect_ratio") or getattr(settings, "kling_default_ratio", "9:16")
        duration = scene_payload.get("duration_seconds") or getattr(settings, "kling_default_duration", 5)

        # Kling variants may accept different field sets depending on model/version.
        # Keep body conservative and pass optional fields only when present.
        body["aspect_ratio"] = aspect_ratio
        body["duration"] = str(duration)

        image_url = scene_payload.get("start_image_url") or scene_payload.get("image_url")
        if mode == "image_to_video":
            if not image_url:
                raise ProviderConfigError("Kling image_to_video requires start_image_url or image_url")
            body["image"] = image_url

        camera_control = scene_payload.get("camera_control")
        if camera_control:
            body["camera_control"] = camera_control

        callback_url = scene_payload.get("callback_url")
        if callback_url:
            body["callback_url"] = callback_url

        return body

    def _extract_task_id(self, raw: dict[str, Any]) -> str | None:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        candidates = [
            raw.get("task_id"),
            raw.get("id"),
            raw.get("request_id"),
            data.get("task_id"),
            data.get("id"),
            data.get("request_id"),
        ]
        for value in candidates:
            if value:
                return str(value)
        return None

    def _extract_status_raw(self, raw: dict[str, Any]) -> str:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        return str(
            data.get("task_status")
            or data.get("status")
            or raw.get("task_status")
            or raw.get("status")
            or ""
        ).lower()

    def _extract_output_url(self, raw: dict[str, Any]) -> str | None:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else raw
        task_result = data.get("task_result") if isinstance(data.get("task_result"), dict) else {}
        videos = task_result.get("videos") if isinstance(task_result.get("videos"), list) else None

        if videos:
            first = videos[0]
            if isinstance(first, dict):
                return (
                    first.get("url")
                    or first.get("video_url")
                    or first.get("resource_url")
                )

        return (
            data.get("video_url")
            or data.get("url")
            or data.get("output_url")
            or raw.get("video_url")
            or raw.get("url")
        )

    def _normalize_state(self, status_raw: str) -> str:
        if status_raw in {"succeed", "succeeded", "success", "completed", "complete"}:
            return "succeeded"
        if status_raw in {"failed", "fail", "error"}:
            return "failed"
        if status_raw in {"cancelled", "canceled"}:
            return "canceled"
        return "processing"

    def _extract_error(self, raw: dict[str, Any]) -> str | None:
        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        message = (
            raw.get("message")
            or raw.get("error")
            or data.get("message")
            or data.get("error")
            or data.get("task_status_msg")
        )
        code = raw.get("code") or data.get("code")
        if code and message:
            return f"{code}: {message}"
        if message:
            return str(message)
        return None

    async def submit(self, scene_payload: dict[str, Any], callback_url: str | None) -> NormalizedSubmitResult:
        if provider_mock_enabled():
            return mock_submit_result(
                provider=self.provider_name,
                model=scene_payload.get("provider_model") or getattr(settings, "kling_default_model", "kling-v2-1"),
                callback_url=callback_url,
                reason="mock_kling_submit",
            )

        mode = self._mode(scene_payload)
        body = self._build_body({**scene_payload, "callback_url": callback_url or scene_payload.get("callback_url")})

        raw = await request_json(
            method="POST",
            url=self._submit_url(mode),
            headers=self._headers(),
            json_body=body,
        )

        task_id = self._extract_task_id(raw)
        status_raw = self._extract_status_raw(raw) or "submitted"
        error = None if task_id else (self._extract_error(raw) or "Kling did not return task id")

        return NormalizedSubmitResult(
            accepted=bool(task_id),
            provider=self.provider_name,
            provider_model=body.get("model_name"),
            provider_task_id=task_id,
            provider_operation_name=mode,
            provider_status_raw=status_raw,
            callback_url_used=callback_url,
            raw_response=raw,
            error_message=error,
        )

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        if provider_mock_enabled():
            return mock_query_result(self.provider_name)

        task_id = provider_task_id
        if not task_id:
            raise ProviderConfigError("Kling query requires provider_task_id")

        mode = provider_operation_name or "text_to_video"
        if mode not in {"text_to_video", "image_to_video"}:
            mode = "image_to_video" if str(mode).lower().find("image") >= 0 else "text_to_video"

        raw = await request_json(
            method="GET",
            url=self._query_url(mode, task_id),
            headers=self._headers(),
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
            or payload.get("request_id")
            or payload.get("id")
            or hashlib.sha256(idem_source.encode("utf-8")).hexdigest()
        )
        task_id = self._extract_task_id(payload)
        return make_callback_event(
            provider=self.provider_name,
            payload=payload,
            event_idempotency_key=event_idempotency_key,
            event_type=str(payload.get("event") or payload.get("type") or "provider_callback"),
            provider_task_id=task_id,
            provider_status_raw=status_raw or None,
            state=self._normalize_state(status_raw),
            output_video_url=self._extract_output_url(payload),
            error_message=self._extract_error(payload),
        )
