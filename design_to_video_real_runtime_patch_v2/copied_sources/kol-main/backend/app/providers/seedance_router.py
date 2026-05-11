import os
from typing import Any, Dict
import requests

from .video_router_base import ProviderCapability, VideoProvider


class SeedanceProvider(VideoProvider):
    name = "seedance"

    def __init__(self) -> None:
        self.enabled = os.getenv("SEEDANCE_ENABLED", "false").lower() == "true"
        self.api_key = os.getenv("ARK_API_KEY", "")
        self.base_url = os.getenv("SEEDANCE_BASE_URL", "https://ark.ap-southeast.bytepluses.com/api/v3").rstrip("/")
        self.text_model = os.getenv("SEEDANCE_TEXT_MODEL", "seedance-1-0-pro")
        self.image_model = os.getenv("SEEDANCE_IMAGE_MODEL", "seedance-1-0-pro")

    def capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            modes={"text_to_video", "image_to_video"},
            enabled=self.enabled and bool(self.api_key),
            priority=10,
            cost_score=0.65,
            latency_score=0.55,
            quality_score=0.75,
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def healthcheck(self) -> bool:
        return self.capability().enabled

    def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mode = payload["mode"]
        model = self.image_model if mode == "image_to_video" else self.text_model
        body = {
            "model": model,
            "prompt": payload["prompt"],
            "duration": payload.get("duration_seconds", 5),
            "aspect_ratio": payload.get("aspect_ratio", "16:9"),
        }
        if mode == "image_to_video":
            body["image_url"] = str(payload["image_url"])

        # Keep endpoint configurable because BytePlus video endpoints may vary by enabled model/product.
        endpoint = os.getenv("SEEDANCE_CREATE_TASK_PATH", "/contents/generations/tasks")
        resp = requests.post(f"{self.base_url}{endpoint}", headers=self._headers(), json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("id") or data.get("task_id") or data.get("data", {}).get("id")
        if not task_id:
            raise RuntimeError(f"Seedance task id missing: {data}")
        return {"provider": self.name, "external_task_id": task_id, "status": data.get("status", "submitted"), "raw": data}

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = os.getenv("SEEDANCE_GET_TASK_PATH_TEMPLATE", "/contents/generations/tasks/{task_id}")
        resp = requests.get(f"{self.base_url}{endpoint.format(task_id=task_id)}", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()
