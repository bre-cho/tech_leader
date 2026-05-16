"""
Bytedance Seedance 2.0 client via kie.ai marketplace.

API reference: https://docs.kie.ai/market/bytedance/seedance-2

Flow:
    1. POST /api/v1/jobs/createTask  → returns taskId
    2. POST /api/v1/jobs/recordInfo  → poll by taskId
    3. Response contains media URL (video_url / resultUrl)

Security:
  - API key is read ONLY from backend env var SEEDANCE_API_KEY.
  - NEVER put SEEDANCE_API_KEY in Next.js .env.local or Vite .env.
  - All Kie AI calls are made from this backend module, never from the frontend.
"""
from __future__ import annotations

import time
from typing import Any, Literal, Optional

import httpx

from app.vendor.seedance2.config import seedance_config

_DEFAULT_POLL_INTERVAL = 5   # seconds between polls
_DEFAULT_TIMEOUT = 1200       # max seconds to wait for completion


class Seedance2Error(Exception):
    """Raised when the kie.ai API returns an error or times out."""


class Seedance2Client:
    """
    Thin synchronous wrapper around the kie.ai Seedance 2 API.

    Reads configuration exclusively from backend env vars via SeedanceConfig:
        SEEDANCE_API_KEY, SEEDANCE_API_BASE_URL, SEEDANCE_MODEL
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        # api_key param is kept for testability only; production always uses env var.
        resolved_key = api_key or seedance_config.api_key
        self._api_key = resolved_key
        self._api_base = seedance_config.api_base_url
        self._model = seedance_config.model
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        *,
        image_url: Optional[str] = None,
        aspect_ratio: str = "16:9",
        duration: Literal[3, 5, 10] = 5,
        resolution: str = "720p",
        model: Optional[str] = None,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        poll_interval: int = _DEFAULT_POLL_INTERVAL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> dict[str, Any]:
        """
        Submit a generation job and block until it completes.

        Returns the completed task dict from kie.ai including ``video_url``.
        """
        task_id = self._submit(
            prompt=prompt,
            image_url=image_url,
            aspect_ratio=aspect_ratio,
            duration=duration,
            resolution=resolution,
            model=model or self._model,
            negative_prompt=negative_prompt,
            seed=seed,
        )
        return self._poll(task_id, poll_interval=poll_interval, timeout=timeout)

    def submit_async(
        self,
        prompt: str,
        *,
        image_url: Optional[str] = None,
        aspect_ratio: str = "16:9",
        duration: Literal[3, 5, 10] = 5,
        resolution: str = "720p",
        model: Optional[str] = None,
        negative_prompt: str = "",
        seed: Optional[int] = None,
    ) -> str:
        """Submit without blocking. Returns ``task_id`` for later polling."""
        return self._submit(
            prompt=prompt,
            image_url=image_url,
            aspect_ratio=aspect_ratio,
            duration=duration,
            resolution=resolution,
            model=model or self._model,
            negative_prompt=negative_prompt,
            seed=seed,
        )

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Fetch current task state from kie.ai."""
        url = f"{self._api_base}/api/v1/jobs/recordInfo"
        payload = {"taskId": task_id}
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=self._headers, json=payload)
        self._raise_for_status(response, "get_task")
        data = response.json()
        if not isinstance(data, dict):
            raise Seedance2Error(f"Unexpected get_task response shape: {data}")
        return data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _submit(
        self,
        *,
        prompt: str,
        image_url: Optional[str],
        aspect_ratio: str,
        duration: int,
        resolution: str,
        model: str,
        negative_prompt: str,
        seed: Optional[int],
    ) -> str:
        input_payload: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
            "generate_audio": False,
            "web_search": False,
        }
        if image_url:
            input_payload["first_frame_url"] = image_url
        if negative_prompt:
            input_payload["negative_prompt"] = negative_prompt
        if seed is not None:
            input_payload["seed"] = seed

        payload: dict[str, Any] = {
            "model": model,
            "input": input_payload,
        }

        url = f"{self._api_base}/api/v1/jobs/createTask"
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=self._headers, json=payload)
        self._raise_for_status(response, "submit")
        data = response.json()
        if not isinstance(data, dict):
            raise Seedance2Error(f"Unexpected submit response shape: {data}")
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        task_id = (
            data.get("taskId")
            or data.get("task_id")
            or data.get("id")
            or nested.get("taskId")
            or nested.get("task_id")
        )
        if not task_id:
            raise Seedance2Error(f"No task_id in submit response: {data}")
        return str(task_id)

    def _poll(
        self,
        task_id: str,
        *,
        poll_interval: int,
        timeout: int,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            if time.monotonic() > deadline:
                raise Seedance2Error(
                    f"Seedance2 task {task_id} timed out after {timeout}s"
                )
            task = self.get_task(task_id)
            if not isinstance(task, dict):
                raise Seedance2Error(f"Invalid task payload: {task}")
            data = task.get("data") if isinstance(task.get("data"), dict) else task
            status = str(
                data.get("status")
                or data.get("state")
                or data.get("taskStatus")
                or "unknown"
            ).lower()
            if status in {"completed", "success", "succeeded", "done", "finish", "finished"}:
                return task
            if status in {"failed", "error", "cancelled", "canceled", "timeout"}:
                reason = (
                    data.get("error")
                    or data.get("failReason")
                    or task.get("message")
                    or status
                )
                raise Seedance2Error(
                    f"Seedance2 task {task_id} failed: {reason}"
                )
            time.sleep(poll_interval)

    @staticmethod
    def _raise_for_status(response: httpx.Response, action: str) -> None:
        if response.is_success:
            return
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise Seedance2Error(
            f"kie.ai {action} returned {response.status_code}: {detail}"
        )
