from __future__ import annotations

from typing import Any

from app.providers.seedance2.adapter import Seedance2Adapter


def get_seedance2_provider():
    """
    Visual Engine V4 provider registry bridge.

    Add to your provider router:

        from app.services.visual_engine_v4.seedance2_registry_bridge import get_seedance2_provider

        elif provider_key in {"seedance2", "seedance"}:
            adapter = get_seedance2_provider()

    """
    return Seedance2Adapter()


def normalize_seedance2_visual_payload(scene_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Maps Visual Engine V4 scene payload into Seedance2-friendly payload.

    Required Visual Engine V4 locks:
    - Character DNA
    - Style Lock
    - Motion Template
    - CTA
    """
    prompt = (
        scene_payload.get("video_prompt")
        or scene_payload.get("prompt")
        or scene_payload.get("text")
        or ""
    )

    character = scene_payload.get("character", {})
    style = scene_payload.get("style", {})
    motion = scene_payload.get("motion_template") or scene_payload.get("motion") or {}

    return {
        **scene_payload,
        "prompt": (
            f"{prompt}. Same consistent character DNA: {character}. "
            f"Style lock: {style}. Motion template: {motion}. "
            "High-converting ad video, clear CTA, high contrast, no clutter."
        ),
        "negative_prompt": scene_payload.get("negative_prompt")
        or "random face, inconsistent character, flat lighting, cluttered text, watermark, logo",
    }
