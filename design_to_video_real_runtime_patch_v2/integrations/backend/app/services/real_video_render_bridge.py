from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any
from uuid import uuid4


@dataclass
class RenderScenePayload:
    scene_index: int
    prompt: str
    duration_seconds: float
    aspect_ratio: str
    reference_image_url: str | None = None
    voiceover_text: str | None = None
    metadata: dict[str, Any] | None = None


class RealVideoRenderBridge:
    """Bridge từ Design-to-Video MVP sang kol-main-4 render runtime thật.

    Module này giả định bạn đã merge/copied `copied_sources/kol-main/backend/app/**`
    vào backend chính. Khi đó bridge sẽ import trực tiếp service thật:

    - app.services.render_orchestrator
    - app.services.provider_router
    - app.api.production_render_routes / render_execution contracts

    Nếu import fail, bridge trả lỗi rõ ràng để tránh chạy mock ngầm.
    """

    def __init__(self) -> None:
        self.default_provider = os.getenv("VIDEO_PROVIDER_DEFAULT", "runway").strip().lower()
        self.allow_mock = os.getenv("VIDEO_PROVIDER_ALLOW_MOCK", "false").lower() in {"1", "true", "yes", "on"}

    async def create_render_job_from_storyboard(
        self,
        *,
        project_id: str,
        storyboard: list[dict[str, Any]],
        source_image_url: str | None,
        provider: str | None = None,
        aspect_ratio: str = "9:16",
        subtitle_mode: str = "burn",
    ) -> dict[str, Any]:
        selected_provider = (provider or self.default_provider).strip().lower()
        scenes = [asdict(scene) for scene in self._normalize_storyboard(storyboard, source_image_url, aspect_ratio)]

        try:
            from app.services.provider_router import submit_render_task  # type: ignore
        except Exception as exc:  # pragma: no cover - integration guard
            if self.allow_mock:
                return self._local_dev_response(project_id, selected_provider, scenes, str(exc))
            raise RuntimeError(
                "kol-main-4 real render modules are not wired. "
                "Merge copied_sources/kol-main/backend/app into backend/app first."
            ) from exc

        submitted: list[dict[str, Any]] = []
        for scene in scenes:
            result = await submit_render_task(
                provider=selected_provider,
                scene_payload=scene,
                callback_url=os.getenv("VIDEO_PROVIDER_CALLBACK_URL"),
            )
            submitted.append(
                {
                    "scene_index": scene["scene_index"],
                    "provider": selected_provider,
                    "accepted": getattr(result, "accepted", None),
                    "provider_task_id": getattr(result, "provider_task_id", None),
                    "provider_operation_name": getattr(result, "provider_operation_name", None),
                    "raw_response": getattr(result, "raw_response", None),
                    "error_message": getattr(result, "error_message", None),
                }
            )

        return {
            "render_job_id": str(uuid4()),
            "project_id": project_id,
            "provider": selected_provider,
            "aspect_ratio": aspect_ratio,
            "subtitle_mode": subtitle_mode,
            "status": "submitted",
            "scene_count": len(scenes),
            "submitted_scenes": submitted,
        }

    def _normalize_storyboard(
        self,
        storyboard: list[dict[str, Any]],
        source_image_url: str | None,
        aspect_ratio: str,
    ) -> list[RenderScenePayload]:
        normalized: list[RenderScenePayload] = []
        for index, scene in enumerate(storyboard, start=1):
            prompt = scene.get("prompt") or scene.get("visual") or scene.get("description") or scene.get("title")
            if not prompt:
                prompt = f"Cinematic commercial video scene {index} based on selected poster."
            normalized.append(
                RenderScenePayload(
                    scene_index=int(scene.get("scene_index") or index),
                    prompt=str(prompt),
                    duration_seconds=float(scene.get("duration_seconds") or scene.get("duration") or 3.0),
                    aspect_ratio=aspect_ratio,
                    reference_image_url=scene.get("reference_image_url") or source_image_url,
                    voiceover_text=scene.get("voiceover") or scene.get("voiceover_text"),
                    metadata={"source": "design_to_video_mvp", "raw_scene": scene},
                )
            )
        return normalized

    def _local_dev_response(self, project_id: str, provider: str, scenes: list[dict[str, Any]], import_error: str) -> dict[str, Any]:
        return {
            "render_job_id": str(uuid4()),
            "project_id": project_id,
            "provider": provider,
            "status": "dev_mock_blocked_in_production",
            "scene_count": len(scenes),
            "submitted_scenes": [],
            "warning": "Real render module import failed; this response is allowed only because VIDEO_PROVIDER_ALLOW_MOCK=true.",
            "import_error": import_error,
        }
