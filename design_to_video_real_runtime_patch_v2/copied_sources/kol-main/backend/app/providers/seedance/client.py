from __future__ import annotations

import asyncio
import json
import time
from typing import Any
import httpx

from .config import SeedanceRouteConfig
from .types import SeedanceCreateRequest, SeedanceTask, SeedanceTaskStatus, SeedanceMode


_DEFAULT_VIDEO_MODEL_CANDIDATES = (
    "dreamina-seedance-2-0-260128",
    "dreamina-seedance-2-0-fast-260128",
    "seedance-1-5-pro-251215",
    "seedance-1-0-pro-fast-251015",
    "seedance-1-0-pro-250528",
    "seedance-1-0-lite-t2v-250428",
    "seedance-1-0-lite-i2v-250428",
)
_DEFAULT_PROBE_PROMPT = "A cinematic sunset over the ocean"
_DEFAULT_PROBE_IMAGE_URL = "https://ark-doc.tos-ap-southeast-1.bytepluses.com/see_i2v.jpeg"


class SeedanceClient:
    _last_working_model: str | None = None

    def __init__(self, config: SeedanceRouteConfig | None = None):
        self.config = config or SeedanceRouteConfig.from_env()

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _url(self, path: str, **params: str) -> str:
        for key, value in params.items():
            path = path.replace("{" + key + "}", value)
        return f"{self.config.base_url}{path}"

    def _to_provider_payload(self, req: SeedanceCreateRequest, *, model: str | None = None) -> dict[str, Any]:
        # BytePlus ModelArk-style canonical payload. Vendor gateways can override paths/env,
        # but the internal contract remains stable.
        content: list[dict[str, Any]] = [{"type": "text", "text": req.prompt}]
        if req.mode == SeedanceMode.image_to_video and req.image_url:
            content.append({"type": "image_url", "image_url": {"url": str(req.image_url)}})

        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "content": content,
            "metadata": req.metadata,
            "generation_config": {
                "aspect_ratio": req.aspect_ratio,
                "duration": req.duration_seconds,
                "resolution": req.resolution,
                "generate_audio": req.generate_audio,
            },
        }
        if req.negative_prompt:
            payload["generation_config"]["negative_prompt"] = req.negative_prompt
        if req.seed is not None:
            payload["generation_config"]["seed"] = req.seed
        if req.camera_motion:
            payload["generation_config"]["camera_motion"] = req.camera_motion
        return payload

    def _normalize_status(self, raw: dict[str, Any]) -> SeedanceTask:
        task_id = str(raw.get("id") or raw.get("task_id") or raw.get("response_id") or "")
        raw_status = str(raw.get("status") or raw.get("task_status") or raw.get("state") or "unknown").lower()
        status_map = {
            "queued": SeedanceTaskStatus.queued,
            "pending": SeedanceTaskStatus.queued,
            "created": SeedanceTaskStatus.queued,
            "running": SeedanceTaskStatus.running,
            "processing": SeedanceTaskStatus.running,
            "in_progress": SeedanceTaskStatus.running,
            "succeeded": SeedanceTaskStatus.succeeded,
            "success": SeedanceTaskStatus.succeeded,
            "completed": SeedanceTaskStatus.succeeded,
            "failed": SeedanceTaskStatus.failed,
            "error": SeedanceTaskStatus.failed,
            "cancelled": SeedanceTaskStatus.cancelled,
            "canceled": SeedanceTaskStatus.cancelled,
        }
        video_url = None
        for key in ("video_url", "output_url", "url"):
            if raw.get(key):
                video_url = str(raw[key])
                break
        if not video_url:
            output = raw.get("output") or raw.get("result") or {}
            if isinstance(output, dict):
                video_url = output.get("video_url") or output.get("url")
        return SeedanceTask(
            provider_route=self.config.route,
            task_id=task_id,
            status=status_map.get(raw_status, SeedanceTaskStatus.unknown),
            raw_status=raw_status,
            video_url=video_url,
            error_message=str(raw.get("error") or raw.get("message") or "") or None,
            raw=raw,
        )

    @staticmethod
    def _is_video_model(model_info: dict[str, Any]) -> bool:
        if model_info.get("domain") == "VideoGeneration":
            return True
        task_types = model_info.get("task_type") or []
        return any(task_type in {"TextToVideo", "ImageToVideo", "MultimodalToVideo", "VideoEditing", "VideoExtension"} for task_type in task_types)

    async def list_models(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.get(
                self._url("/api/v3/models"),
                headers=self._headers(),
            )
            response.raise_for_status()
            payload = response.json()
        models = payload.get("data") if isinstance(payload, dict) else None
        return models if isinstance(models, list) else []

    async def list_video_models(self) -> list[dict[str, Any]]:
        return [model for model in await self.list_models() if self._is_video_model(model)]

    @staticmethod
    def _extract_error_details(exc: httpx.HTTPStatusError) -> dict[str, Any]:
        try:
            payload = exc.response.json()
        except ValueError:
            payload = {"raw": exc.response.text}
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            return {
                "status_code": exc.response.status_code,
                "error_code": error.get("code"),
                "message": error.get("message") or exc.response.text,
                "raw": payload,
            }
        return {
            "status_code": exc.response.status_code,
            "error_code": None,
            "message": exc.response.text,
            "raw": payload,
        }

    @staticmethod
    def _probe_classification(details: dict[str, Any]) -> str:
        status_code = details.get("status_code")
        error_code = details.get("error_code")
        if status_code in {401, 403}:
            return "auth_error"
        if error_code == "ModelNotOpen":
            return "model_not_open"
        if error_code == "InvalidEndpointOrModel.NotFound":
            return "not_found"
        if status_code == 404:
            return "not_found"
        return "error"

    async def _create_task_once(self, req: SeedanceCreateRequest, *, model: str) -> SeedanceTask:
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(
                self._url(self.config.create_path),
                headers=self._headers(req.idempotency_key),
                json=self._to_provider_payload(req, model=model),
            )
            response.raise_for_status()
            task = self._normalize_status(response.json())
            task.raw.setdefault("selected_model", model)
            return task

    async def _candidate_models(self) -> list[str]:
        candidates: list[str] = []
        if self._last_working_model:
            candidates.append(self._last_working_model)
        candidates.append(self.config.model)
        candidates.extend(self.config.preferred_video_models)
        candidates.extend(_DEFAULT_VIDEO_MODEL_CANDIDATES)
        try:
            candidates.extend(str(item.get("id")) for item in await self.list_video_models() if item.get("id"))
        except httpx.HTTPError:
            pass

        deduped: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            value = str(candidate or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        return deduped

    async def probe_model_access(
        self,
        model: str,
        *,
        prompt: str = _DEFAULT_PROBE_PROMPT,
        image_url: str = _DEFAULT_PROBE_IMAGE_URL,
    ) -> dict[str, Any]:
        mode = SeedanceMode.image_to_video if "i2v" in model else SeedanceMode.text_to_video
        req = SeedanceCreateRequest(
            mode=mode,
            prompt=prompt,
            image_url=image_url if mode == SeedanceMode.image_to_video else None,
            duration_seconds=5,
            resolution="720p",
            metadata={"probe": True},
        )
        try:
            task = await self._create_task_once(req, model=model)
            self.__class__._last_working_model = model
            return {
                "model": model,
                "classification": "usable",
                "task_id": task.task_id,
                "raw_status": task.raw_status,
                "provider_route": task.provider_route,
                "raw": task.raw,
            }
        except httpx.HTTPStatusError as exc:
            details = self._extract_error_details(exc)
            return {
                "model": model,
                "classification": self._probe_classification(details),
                **details,
            }

    async def probe_video_models(
        self,
        *,
        stop_on_first_usable: bool = False,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for model in await self._candidate_models():
            result = await self.probe_model_access(model)
            results.append(result)
            if stop_on_first_usable and result.get("classification") == "usable":
                break
        return results

    async def create_task(self, req: SeedanceCreateRequest) -> SeedanceTask:
        candidate_errors: list[dict[str, Any]] = []
        for model in await self._candidate_models():
            try:
                task = await self._create_task_once(req, model=model)
                self.__class__._last_working_model = model
                return task
            except httpx.HTTPStatusError as exc:
                details = self._extract_error_details(exc)
                details["model"] = model
                candidate_errors.append(details)
                if self._probe_classification(details) in {"model_not_open", "not_found"}:
                    continue
                raise

        summary = json.dumps(candidate_errors[:5], ensure_ascii=False)
        raise RuntimeError(f"No activated Seedance video model found. probe_summary={summary}")

    async def retrieve_task(self, task_id: str) -> SeedanceTask:
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.get(
                self._url(self.config.retrieve_path, task_id=task_id),
                headers=self._headers(),
            )
            response.raise_for_status()
            return self._normalize_status(response.json())

    async def cancel_task(self, task_id: str) -> SeedanceTask:
        if not self.config.cancel_path:
            raise RuntimeError("Seedance cancel path is not configured")
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.delete(
                self._url(self.config.cancel_path, task_id=task_id),
                headers=self._headers(),
            )
            response.raise_for_status()
            return self._normalize_status(response.json())

    async def poll_until_done(self, task_id: str) -> SeedanceTask:
        deadline = time.time() + self.config.max_poll_seconds
        last = await self.retrieve_task(task_id)
        while time.time() < deadline and last.status in {SeedanceTaskStatus.queued, SeedanceTaskStatus.running, SeedanceTaskStatus.unknown}:
            await asyncio.sleep(self.config.poll_interval_seconds)
            last = await self.retrieve_task(task_id)
        return last
