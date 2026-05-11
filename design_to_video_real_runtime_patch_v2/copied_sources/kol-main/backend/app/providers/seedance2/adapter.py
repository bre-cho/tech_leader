from __future__ import annotations

import hashlib
import json
import os
from typing import Any

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
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)
from .payload_builder import Seedance2RenderSpec, build_seedance2_payload
from .status_mapper import normalize_seedance2_status


class Seedance2Adapter(BaseVideoProviderAdapter):
    """Production-oriented Seedance2 adapter scaffold.

    Endpoint names may need adjustment to match the official account/API gateway.
    Keep normalized return shape stable for the rest of the render pipeline.
    """

    provider_name = "seedance2"

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout_s: float = 60.0):
        self.api_key = api_key or os.getenv("SEEDANCE2_API_KEY")
        self.base_url = (base_url or os.getenv("SEEDANCE2_BASE_URL") or "").rstrip("/")
        self.timeout_s = timeout_s
        self.default_model = os.getenv("SEEDANCE2_DEFAULT_MODEL", "seedance-2.0")

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _require_config(self) -> None:
        if not self.api_key:
            raise ProviderConfigError("SEEDANCE2_API_KEY is required")
        if not self.base_url:
            raise ProviderConfigError("SEEDANCE2_BASE_URL is required")

    def _build_spec(self, scene_payload: dict[str, Any], callback_url: str | None) -> Seedance2RenderSpec:
        prompt = (
            scene_payload.get("prompt")
            or scene_payload.get("video_prompt")
            or scene_payload.get("text")
            or ""
        )
        if not prompt.strip():
            raise ProviderConfigError("Seedance2 render requires prompt/video_prompt/text")

        operation_type = str(scene_payload.get("mode") or scene_payload.get("operation_type") or "text_to_video")
        image_refs = list(scene_payload.get("reference_images") or [])
        video_refs = list(scene_payload.get("reference_videos") or [])
        if scene_payload.get("start_image_url"):
            image_refs.append(scene_payload["start_image_url"])
        if scene_payload.get("image_url"):
            image_refs.append(scene_payload["image_url"])
        if scene_payload.get("input_video_url"):
            video_refs.append(scene_payload["input_video_url"])

        if operation_type == "text_to_video" and image_refs:
            operation_type = "image_to_video"
        if operation_type == "text_to_video" and video_refs:
            operation_type = "video_to_video"

        return Seedance2RenderSpec(
            prompt=prompt,
            operation_type=operation_type,
            model=str(scene_payload.get("provider_model") or self.default_model),
            duration_sec=int(scene_payload.get("duration_seconds") or 5),
            aspect_ratio=str(scene_payload.get("aspect_ratio") or "16:9"),
            resolution=str(scene_payload.get("resolution") or "1080p"),
            negative_prompt=scene_payload.get("negative_prompt"),
            reference_images=image_refs,
            reference_videos=video_refs,
            reference_audio=list(scene_payload.get("reference_audio") or []),
            edit_instruction=scene_payload.get("edit_instruction"),
            seed=scene_payload.get("seed"),
            callback_url=callback_url,
            idempotency_key=scene_payload.get("idempotency_key"),
            metadata=scene_payload.get("metadata") or {},
        )

    async def submit(self, scene_payload: dict[str, Any], callback_url: str | None) -> NormalizedSubmitResult:
        model = scene_payload.get("provider_model") or self.default_model
        if provider_mock_enabled():
            return mock_submit_result(
                provider=self.provider_name,
                model=model,
                callback_url=callback_url,
                reason="mock_seedance2_submit",
            )

        self._require_config()
        spec = self._build_spec(scene_payload, callback_url)
        payload = build_seedance2_payload(spec)
        raw = await request_json(
            method="POST",
            url=f"{self.base_url}/video/generations",
            json_body=payload,
            headers=self._headers(spec.idempotency_key),
            timeout_seconds=int(self.timeout_s),
        )

        job_id = raw.get("id") or raw.get("job_id") or raw.get("task_id")
        status_raw = str(raw.get("status") or raw.get("state") or "submitted")
        return NormalizedSubmitResult(
            accepted=bool(job_id),
            provider=self.provider_name,
            provider_model=str(spec.model),
            provider_task_id=str(job_id) if job_id else None,
            provider_operation_name=spec.operation_type,
            provider_status_raw=status_raw,
            idempotency_key=spec.idempotency_key,
            callback_url_used=callback_url,
            raw_response=raw,
            error_message=None if job_id else "Seedance2 did not return task id",
        )

    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        if provider_mock_enabled():
            return mock_query_result(self.provider_name)

        self._require_config()
        if not provider_task_id:
            raise ProviderConfigError("Seedance2 query requires provider_task_id")

        raw = await request_json(
            method="GET",
            url=f"{self.base_url}/video/generations/{provider_task_id}",
            headers=self._headers(),
            timeout_seconds=int(self.timeout_s),
        )
        normalized = normalize_seedance2_status(raw)
        state_raw = str(normalized.get("status") or "processing")
        state = "processing" if state_raw in {"running", "unknown"} else state_raw
        return NormalizedStatusResult(
            provider=self.provider_name,
            state=state,
            provider_status_raw=str(normalized.get("provider_status") or ""),
            output_video_url=normalized.get("output_url"),
            error_message=normalized.get("error"),
            raw_response=raw,
            metadata={
                "provider_task_id": provider_task_id,
                "provider_operation_name": provider_operation_name,
            },
        )

    def verify_callback(self, headers: dict[str, str], raw_body: bytes) -> bool:
        return verify_hmac_signature(
            headers=headers,
            raw_body=raw_body,
            secret=os.getenv("SEEDANCE2_CALLBACK_SECRET") or os.getenv("PROVIDER_CALLBACK_SHARED_SECRET"),
        )

    def normalize_callback(self, headers: dict[str, str], payload: dict) -> NormalizedCallbackEvent:
        task_id = str(payload.get("task_id") or payload.get("id") or "") or None
        status_raw = str(payload.get("status") or payload.get("state") or "processing")
        state = normalize_seedance2_status(payload).get("status") or "processing"
        idem_source = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        event_idempotency_key = str(
            payload.get("event_id")
            or payload.get("request_id")
            or task_id
            or hashlib.sha256(idem_source.encode("utf-8")).hexdigest()
        )
        return make_callback_event(
            provider=self.provider_name,
            payload=payload,
            event_idempotency_key=event_idempotency_key,
            event_type=str(payload.get("event") or payload.get("type") or "provider_callback"),
            provider_task_id=task_id,
            provider_status_raw=status_raw,
            state="processing" if state in {"running", "unknown"} else state,
            output_video_url=normalize_seedance2_status(payload).get("output_url"),
            error_message=normalize_seedance2_status(payload).get("error"),
        )
