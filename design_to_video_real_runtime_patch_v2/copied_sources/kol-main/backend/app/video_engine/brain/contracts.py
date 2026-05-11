from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class BrainMode(str, Enum):
    text_to_video = "text_to_video"
    image_to_video = "image_to_video"
    video_to_video = "video_to_video"
    reference_to_video = "reference_to_video"
    video_edit = "video_edit"
    video_extend = "video_extend"


class QualityTier(str, Enum):
    draft = "draft"
    standard = "standard"
    premium = "premium"


class BrainAudioOptions(BaseModel):
    enabled: bool = False
    prompt: Optional[str] = None
    reference_audio_url: Optional[HttpUrl] = None


class MultiModalReference(BaseModel):
    kind: str = Field(..., description="image|video|audio")
    url: str
    role: str = Field(default="general", description="subject|style|camera|motion|audio|environment")
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class MultiModalVideoIntent(BaseModel):
    raw_prompt: str
    subject: str = ""
    motion: str = ""
    environment: str = ""
    aesthetics: str = ""
    camera: str = ""
    audio: str = ""
    negative_prompt: str = ""
    mode: BrainMode = BrainMode.text_to_video
    aspect_ratio: str = "16:9"
    duration_seconds: int = Field(default=8, ge=1, le=60)
    quality_tier: QualityTier = QualityTier.standard
    seed: Optional[int] = None
    references: List[MultiModalReference] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderCapability(BaseModel):
    provider: str
    models: List[str] = Field(default_factory=list)
    modes: List[str] = Field(default_factory=list)
    aspect_ratios: List[str] = Field(default_factory=list)
    max_duration_seconds: int = 8
    supports_audio: bool = False
    supports_image_reference: bool = False
    supports_video_reference: bool = False
    supports_audio_reference: bool = False
    supports_video_editing: bool = False
    supports_video_extension: bool = False
    supports_text_overlay: bool = False
    estimated_cost_per_second: float = 0.0
    estimated_latency_ms: float = 60000.0
    quality_bias: float = 0.5
    draft_model: Optional[str] = Field(
        default=None,
        description=(
            "Explicit model name to use when quality_tier='draft'. "
            "When set, _select_model() uses this directly instead of guessing from model name strings. "
            "Should reference one of the entries in ``models``."
        ),
    )


class ProviderDecision(BaseModel):
    selected_provider: str
    selected_model: Optional[str] = None
    decision_reason: str
    fallback_chain: List[str] = Field(default_factory=list)
    rejected: List[Dict[str, Any]] = Field(default_factory=list)
    scorecard: Dict[str, Any] = Field(default_factory=dict)


class CompiledProviderPayload(BaseModel):
    provider: str
    model: Optional[str] = None
    mode: str
    prompt: str
    negative_prompt: Optional[str] = None
    aspect_ratio: str
    duration_seconds: int
    seed: Optional[int] = None
    references: List[Dict[str, Any]] = Field(default_factory=list)
    audio: Dict[str, Any] = Field(default_factory=dict)
    provider_options: Dict[str, Any] = Field(default_factory=dict)


class BrainPlan(BaseModel):
    intent: MultiModalVideoIntent
    selected_provider: str
    selected_model: Optional[str] = None
    decision_reason: str
    fallback_chain: List[str] = Field(default_factory=list)
    compiled_payload: CompiledProviderPayload
    rejected: List[Dict[str, Any]] = Field(default_factory=list)
    scorecard: Dict[str, Any] = Field(default_factory=dict)


# Visual Engine V4 bridge compatibility contracts
from pydantic import BaseModel, Field
from typing import Any

class BrainDecisionRequest(BaseModel):
    project_id: str
    scene_id: str
    goal: str = "video_ad"
    platform: str = "tiktok_facebook"
    requested_provider: str | None = None
    target_mode: str = "text_to_video"
    prompt: str
    character_dna: dict[str, Any] = Field(default_factory=dict)
    style_lock: dict[str, Any] = Field(default_factory=dict)
    motion_template: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrainDecisionResult(BaseModel):
    provider: str
    mode: str
    reason: str
    confidence: float = 0.0
    compiled_prompt: dict[str, Any] = Field(default_factory=dict)
    fallback_providers: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
