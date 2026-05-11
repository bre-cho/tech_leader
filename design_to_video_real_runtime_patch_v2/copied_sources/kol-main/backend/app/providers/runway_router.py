import os
from typing import Any, Dict
import requests

from .video_router_base import ProviderCapability, VideoProvider


class RunwayProvider(VideoProvider):
    name = "runway"

    def __init__(self) -> None:
        self.enabled = os.getenv("RUNWAY_ENABLED", "false").lower() == "true"
        self.api_key = os.getenv("RUNWAYML_API_SECRET", "")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com").rstrip("/")
        self.model = os.getenv("RUNWAY_IMAGE_TO_VIDEO_MODEL", "gen4_turbo")

    def capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            modes={"image_to_video"},
            enabled=self.enabled and bool(self.api_key),
            priority=20,
            cost_score=0.45,
            latency_score=0.60,
            quality_score=0.85,
        )

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def healthcheck(self) -> bool:
        return self.capability().enabled

    def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload["mode"] != "image_to_video":
            raise ValueError("RunwayProvider supports image_to_video only in this patch")
        body = {
            "model": self.model,
            "promptImage": str(payload["image_url"]),
            "promptText": payload["prompt"],
            "ratio": payload.get("aspect_ratio", "16:9"),
        }
        endpoint = os.getenv("RUNWAY_CREATE_TASK_PATH", "/v1/image_to_video")
        resp = requests.post(f"{self.base_url}{endpoint}", headers=self._headers(), json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("id") or data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Runway task id missing: {data}")
        return {"provider": self.name, "external_task_id": task_id, "status": data.get("status", "submitted"), "raw": data}

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = os.getenv("RUNWAY_GET_TASK_PATH_TEMPLATE", "/v1/tasks/{task_id}")
        resp = requests.get(f"{self.base_url}{endpoint.format(task_id=task_id)}", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()
