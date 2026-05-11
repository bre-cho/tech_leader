import os
import time
import jwt
import requests
from typing import Any, Dict

from .video_router_base import ProviderCapability, VideoProvider


class KlingProvider(VideoProvider):
    name = "kling"

    def __init__(self) -> None:
        self.enabled = os.getenv("KLING_ENABLED", "false").lower() == "true"
        self.access_key = os.getenv("KLING_ACCESS_KEY", "")
        self.secret_key = os.getenv("KLING_SECRET_KEY", "")
        self.base_url = os.getenv("KLING_BASE_URL", "https://api.klingai.com").rstrip("/")
        self.model = os.getenv("KLING_IMAGE_TO_VIDEO_MODEL", "kling-v1-6")

    def capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            modes={"image_to_video"},
            enabled=self.enabled and bool(self.access_key) and bool(self.secret_key),
            priority=30,
            cost_score=0.55,
            latency_score=0.50,
            quality_score=0.80,
        )

    def _token(self) -> str:
        now = int(time.time())
        return jwt.encode(
            {"iss": self.access_key, "exp": now + 1800, "nbf": now - 5},
            self.secret_key,
            algorithm="HS256",
        )

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"}

    def healthcheck(self) -> bool:
        return self.capability().enabled

    def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload["mode"] != "image_to_video":
            raise ValueError("KlingProvider supports image_to_video only in this patch")
        body = {
            "model_name": self.model,
            "image": str(payload["image_url"]),
            "prompt": payload["prompt"],
            "duration": payload.get("duration_seconds", 5),
        }
        endpoint = os.getenv("KLING_CREATE_TASK_PATH", "/v1/videos/image2video")
        resp = requests.post(f"{self.base_url}{endpoint}", headers=self._headers(), json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("data", {}).get("task_id") or data.get("task_id") or data.get("id")
        if not task_id:
            raise RuntimeError(f"Kling task id missing: {data}")
        return {"provider": self.name, "external_task_id": task_id, "status": data.get("status", "submitted"), "raw": data}

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = os.getenv("KLING_GET_TASK_PATH_TEMPLATE", "/v1/videos/image2video/{task_id}")
        resp = requests.get(f"{self.base_url}{endpoint.format(task_id=task_id)}", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()
