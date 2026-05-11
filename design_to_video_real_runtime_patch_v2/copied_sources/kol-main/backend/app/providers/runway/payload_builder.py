from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.providers.common import ProviderConfigError


def runway_mode(scene_payload: dict[str, Any]) -> str:
    """
    Gen-4.5 supports text-to-video by omitting promptImage.
    Image-to-video uses promptImage/start image.
    """
    if scene_payload.get("input_video_url"):
        return "video_to_video"
    if scene_payload.get("start_image_url") or scene_payload.get("image_url") or scene_payload.get("promptImage"):
        return "image_to_video"
    return "text_to_video"


def runway_prompt(scene_payload: dict[str, Any]) -> str:
    prompt = (
        scene_payload.get("video_prompt")
        or scene_payload.get("prompt")
        or scene_payload.get("text")
        or ""
    ).strip()

    if not prompt:
        raise ProviderConfigError("Runway render requires video_prompt/prompt/text")
    return prompt


def build_runway_body(scene_payload: dict[str, Any]) -> dict[str, Any]:
    mode = runway_mode(scene_payload)

    body: dict[str, Any] = {
        "model": scene_payload.get("provider_model")
        or getattr(settings, "runway_default_model", "gen4.5"),
        "promptText": runway_prompt(scene_payload),
        "ratio": scene_payload.get("aspect_ratio")
        or getattr(settings, "runway_default_ratio", "1280:720"),
        "duration": scene_payload.get("duration_seconds")
        or getattr(settings, "runway_default_duration", 5),
    }

    seed = scene_payload.get("seed")
    if seed is not None:
        body["seed"] = seed

    # Optional safety/production metadata. Ignored by some endpoints/gateways.
    if scene_payload.get("watermark") is not None:
        body["watermark"] = bool(scene_payload["watermark"])

    image_url = (
        scene_payload.get("promptImage")
        or scene_payload.get("start_image_url")
        or scene_payload.get("image_url")
    )
    if mode == "image_to_video":
        if not image_url:
            raise ProviderConfigError("Runway image_to_video requires start_image_url/image_url/promptImage")
        body["promptImage"] = image_url

    video_url = scene_payload.get("input_video_url")
    if mode == "video_to_video":
        if not video_url:
            raise ProviderConfigError("Runway video_to_video requires input_video_url")
        body["videoUri"] = video_url

    return body
