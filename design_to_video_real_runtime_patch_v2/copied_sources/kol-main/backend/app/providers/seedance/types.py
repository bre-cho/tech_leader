from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SeedanceMode(str, Enum):
    text_to_video = "text_to_video"
    image_to_video = "image_to_video"


class SeedanceCreateRequest(BaseModel):
    mode: SeedanceMode
    prompt: str = Field(min_length=1, max_length=5000)
    image_url: HttpUrl | None = None
    negative_prompt: str | None = None
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] = "16:9"
    duration_seconds: int = Field(default=5, ge=3, le=20)
    resolution: Literal["480p", "720p", "1080p"] = "720p"
    seed: int | None = None
    camera_motion: str | None = None
    generate_audio: bool = False
    idempotency_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("image_url")
    @classmethod
    def image_required_for_i2v(cls, value, info):
        mode = info.data.get("mode")
        if mode == SeedanceMode.image_to_video and value is None:
            raise ValueError("image_url is required for image_to_video")
        return value


class SeedanceTaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"
    unknown = "unknown"


class SeedanceTask(BaseModel):
    provider: str = "seedance"
    provider_route: str
    task_id: str
    status: SeedanceTaskStatus
    raw_status: str | None = None
    video_url: str | None = None
    error_message: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
