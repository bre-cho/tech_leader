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
    verify_hmac_signature,
)
from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)

from .client import SeedanceClient
from .types import SeedanceCreateRequest, SeedanceMode, SeedanceTaskStatus


class SeedanceAdapter(BaseVideoProviderAdapter):
    provider_name = "seedance"

    def _build_request(self, scene_payload: dict[str, Any], callback_url: str | None) -> SeedanceCreateRequest:
        mode = SeedanceMode.image_to_video if scene_payload.get("image_url") or scene_payload.get("start_image_url") else SeedanceMode.text_to_video
        prompt = (
            scene_payload.get("prompt")
            or scene_payload.get("video_prompt")
            or scene_payload.get("text")
            or ""
        )
        if not str(prompt).strip():
            raise ProviderConfigError("Seedance render requires prompt/video_prompt/text")

        idempotency_key = scene_payload.get("idempotency_key")
        if not idempotency_key:
            basis = json.dumps(scene_payload, ensure_ascii=False, sort_keys=True, default=str)
            idempotency_key = "seedance:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()

        metadata = dict(scene_payload.get("metadata") or {})
        if callback_url:
            metadata.setdefault("callback_url", callback_url)

        return SeedanceCreateRequest(
            mode=mode,
            prompt=str(prompt),
            image_url=scene_payload.get("image_url") or scene_payload.get("start_image_url"),
            negative_prompt=scene_payload.get("negative_prompt"),
            aspect_ratio=scene_payload.get("aspect_ratio") or "16:9",
            duration_seconds=int(scene_payload.get("duration_seconds") or 5),
            resolution=scene_payload.get("resolution") or "720p",
            seed=scene_payload.get("seed"),
            camera_motion=scene_payload.get("camera_motion"),
            generate_audio=bool(scene_payload.get("generate_audio", False)),
            idempotency_key=idempotency_key,
            metadata=metadata,
        )

    @staticmethod
    def _state_from_task_status(status: SeedanceTaskStatus) -> str:
        if status == SeedanceTaskStatus.succeeded:
            return "succeeded"
        if status == SeedanceTaskStatus.failed:
            return "failed"
        if status == SeedanceTaskStatus.cancelled:
            return "canceled"
        return "processing"

    async def submit(self, scene_payload: dict, callback_url: str | None) -> NormalizedSubmitResult:
        if provider_mock_enabled():
            return mock_submit_result(
                provider=self.provider_name,
                model=os.getenv("SEEDANCE_MODEL", "seedance-2-0"),
                callback_url=callback_url,
                reason="mock_seedance_submit",
            )

        req = self._build_request(scene_payload, callback_url)
        task = await SeedanceClient().create_task(req)
        return NormalizedSubmitResult(
            accepted=bool(task.task_id),
            provider=self.provider_name,
            provider_model=os.getenv("SEEDANCE_MODEL", "seedance-2-0"),
            provider_task_id=task.task_id,
            provider_operation_name=req.mode.value,
            provider_status_raw=task.raw_status,
            idempotency_key=req.idempotency_key,
            callback_url_used=callback_url,
            raw_response=task.raw,
            error_message=task.error_message,
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
            raise ProviderConfigError("Seedance query requires provider_task_id")

        task = await SeedanceClient().retrieve_task(provider_task_id)
        return NormalizedStatusResult(
            provider=self.provider_name,
            state=self._state_from_task_status(task.status),
            provider_status_raw=task.raw_status,
            output_video_url=task.video_url,
            error_message=task.error_message,
            raw_response=task.raw,
            metadata={"provider_route": task.provider_route},
        )

    def verify_callback(self, headers: dict[str, str], raw_body: bytes) -> bool:
        return verify_hmac_signature(
            headers=headers,
            raw_body=raw_body,
            secret=os.getenv("SEEDANCE_WEBHOOK_SECRET") or os.getenv("PROVIDER_CALLBACK_SHARED_SECRET"),
        )

    def normalize_callback(self, headers: dict[str, str], payload: dict) -> NormalizedCallbackEvent:
        task_id = str(payload.get("task_id") or payload.get("id") or "") or None
        status_raw = str(payload.get("status") or payload.get("task_status") or payload.get("state") or "unknown")
        state = "processing"
        lowered = status_raw.lower()
        if lowered in {"succeeded", "success", "completed"}:
            state = "succeeded"
        elif lowered in {"failed", "error"}:
            state = "failed"
        elif lowered in {"cancelled", "canceled"}:
            state = "canceled"

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
            state=state,
            output_video_url=payload.get("video_url") or payload.get("output_url") or payload.get("url"),
            error_message=payload.get("error") or payload.get("message"),
        )
