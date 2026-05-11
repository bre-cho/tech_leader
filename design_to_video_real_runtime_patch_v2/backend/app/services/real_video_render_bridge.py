from __future__ import annotations

import os
from typing import Any, Dict, List
from uuid import uuid4


class RealVideoRenderBridge:
    SUPPORTED_PROVIDERS = {
        "veo",
        "veo_3",
        "veo_3_1",
        "runway",
        "kling",
        "seedance",
        "seedance2",
        "volcengine",
    }

    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development").lower()
        self.render_mode = os.getenv("VIDEO_RENDER_MODE", "real_provider")
        self.default_provider = os.getenv("VIDEO_PROVIDER_DEFAULT", "runway")
        self.allow_mock = os.getenv("VIDEO_PROVIDER_ALLOW_MOCK", "false").lower() == "true"

    def _validate_env_policy(self) -> None:
        if self.render_mode != "real_provider":
            raise RuntimeError("VIDEO_RENDER_MODE must be real_provider")
        if self.app_env == "production" and self.allow_mock:
            raise RuntimeError("VIDEO_PROVIDER_ALLOW_MOCK must be false in production")

    def _route_provider(self, payload: Dict[str, Any]) -> str:
        industry = str(payload.get("industry", "")).lower()
        product = str(payload.get("product", "")).lower()

        if industry in {"mỹ phẩm", "my pham", "thời trang", "thoi trang", "f&b", "food", "beverage"}:
            return "runway"
        if industry in {"bất động sản", "bat dong san", "real estate", "cinematic"}:
            return "veo"
        if "showcase" in product or "product" in product:
            return "kling"
        if industry in {"du lịch", "du lich", "story", "narrative"}:
            return "seedance"
        return self.default_provider

    def _ensure_provider_supported(self, provider: str) -> None:
        if provider not in self.SUPPORTED_PROVIDERS:
            raise RuntimeError(f"Unsupported provider: {provider}")

    def build_render_request(self, project_id: str, trace_id: str, storyboard: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_env_policy()
        provider = self._route_provider(payload)
        self._ensure_provider_supported(provider)
        scenes = storyboard.get("scenes", [])
        return {
            "project_id": project_id,
            "trace_id": trace_id,
            "provider": provider,
            "scene_count": len(scenes),
            "scene_tasks": [
                {
                    "scene": scene.get("scene"),
                    "duration": scene.get("duration", 3),
                    "prompt": scene.get("prompt", ""),
                }
                for scene in scenes
            ],
            "poll_policy": {"max_attempts": 15, "interval_seconds": 6},
            "retry_policy": {"max_retries": 2, "strategy": "exponential_backoff"},
            "recovery_policy": {"enabled": True, "mode": "scene_requeue"},
        }

    def create_render_project(self, project_id: str, trace_id: str, storyboard: List[Dict[str, Any]], payload: Dict[str, Any]) -> Dict[str, Any]:
        request_payload = self.build_render_request(
            project_id=project_id,
            trace_id=trace_id,
            storyboard={"scenes": storyboard},
            payload=payload,
        )
        render_job_id = str(uuid4())
        return {
            "render_job_id": render_job_id,
            "status": "queued",
            "provider": request_payload["provider"],
            "callback_expected": True,
            "polling_enabled": True,
            "artifact_lineage": {
                "step": "render.project.created",
                "parent_step_id": payload.get("parent_step_id"),
                "artifact_id": render_job_id,
            },
            "request": request_payload,
        }
