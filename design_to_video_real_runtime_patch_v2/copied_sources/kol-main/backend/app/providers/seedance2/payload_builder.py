from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SUPPORTED_ASPECT_RATIOS = {"16:9", "9:16", "4:3", "3:4", "21:9", "1:1"}
SUPPORTED_DURATIONS = set(range(4, 16))


@dataclass
class Seedance2RenderSpec:
    prompt: str
    operation_type: str = "text_to_video"
    model: str = "seedance-2.0"
    duration_sec: int = 5
    aspect_ratio: str = "16:9"
    resolution: str = "1080p"
    negative_prompt: str | None = None
    reference_images: list[str] = field(default_factory=list)
    reference_videos: list[str] = field(default_factory=list)
    reference_audio: list[str] = field(default_factory=list)
    edit_instruction: str | None = None
    extend_seconds: int | None = None
    seed: int | None = None
    callback_url: str | None = None
    idempotency_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_seedance2_spec(spec: Seedance2RenderSpec) -> None:
    if not spec.prompt or not spec.prompt.strip():
        raise ValueError("Seedance2 prompt is required")
    if spec.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        raise ValueError(f"Unsupported Seedance2 aspect_ratio: {spec.aspect_ratio}")
    if spec.duration_sec not in SUPPORTED_DURATIONS:
        raise ValueError("Seedance2 duration_sec must be between 4 and 15")
    if spec.operation_type in {"image_to_video", "reference_to_video"} and not spec.reference_images:
        raise ValueError(f"{spec.operation_type} requires reference_images")
    if spec.operation_type in {"video_to_video", "video_edit", "video_extend"} and not spec.reference_videos:
        raise ValueError(f"{spec.operation_type} requires reference_videos")
    if spec.operation_type == "video_edit" and not spec.edit_instruction:
        raise ValueError("video_edit requires edit_instruction")


def build_seedance2_payload(spec: Seedance2RenderSpec) -> dict[str, Any]:
    validate_seedance2_spec(spec)
    payload: dict[str, Any] = {
        "model": spec.model,
        "operation_type": spec.operation_type,
        "prompt": spec.prompt.strip(),
        "render": {
            "duration_sec": spec.duration_sec,
            "aspect_ratio": spec.aspect_ratio,
            "resolution": spec.resolution,
        },
        "references": {
            "images": spec.reference_images,
            "videos": spec.reference_videos,
            "audio": spec.reference_audio,
        },
        "metadata": spec.metadata,
    }
    if spec.negative_prompt:
        payload["negative_prompt"] = spec.negative_prompt
    if spec.edit_instruction:
        payload["edit_instruction"] = spec.edit_instruction
    if spec.extend_seconds:
        payload["extend_seconds"] = spec.extend_seconds
    if spec.seed is not None:
        payload["seed"] = spec.seed
    if spec.callback_url:
        payload["callback_url"] = spec.callback_url
    if spec.idempotency_key:
        payload["idempotency_key"] = spec.idempotency_key
    return payload
