from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class VideoMode(str, Enum):
    text_to_video = "text_to_video"
    image_to_video = "image_to_video"


class VideoRouterRequest(BaseModel):
    mode: VideoMode
    prompt: str = Field(..., min_length=1)
    image_url: Optional[HttpUrl] = None
    duration_seconds: Optional[int] = Field(default=5, ge=1, le=30)
    aspect_ratio: Optional[str] = "16:9"
    provider_hint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderTask(BaseModel):
    provider: str
    external_task_id: str
    status: str
    raw: Dict[str, Any] = Field(default_factory=dict)


class VideoRouterResponse(BaseModel):
    selected_provider: str
    mode: VideoMode
    task: ProviderTask
    fallback_chain: List[str] = Field(default_factory=list)
