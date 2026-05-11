from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, conint


class DurationPreset(int, Enum):
    s15 = 15
    s30 = 30


class StoryboardVariant(str, Enum):
    trust = "trust"
    viral = "viral"
    conversion = "conversion"


class ProviderName(str, Enum):
    veo = "veo"
    runway = "runway"
    kling = "kling"
    seedance = "seedance"
    seedance2 = "seedance2"


class CampaignBrief(BaseModel):
    brand: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    industry: str = Field(default="general")
    target_audience: Optional[str] = None
    goal: str = Field(default="conversion")
    duration: DurationPreset = DurationPreset.s15
    platform: str = Field(default="tiktok_reels_shorts")
    style: str = Field(default="cinematic commercial")
    language: str = Field(default="en")
    aspect_ratio: str = Field(default="9:16")


class PosterInput(BaseModel):
    poster_image_url: Optional[HttpUrl] = None
    poster_image_base64: Optional[str] = None
    campaign_brief: CampaignBrief
    requested_variants: List[StoryboardVariant] = Field(default_factory=lambda: [StoryboardVariant.conversion])
    providers: List[ProviderName] = Field(
        default_factory=lambda: [
            ProviderName.veo,
            ProviderName.runway,
            ProviderName.kling,
            ProviderName.seedance,
            ProviderName.seedance2,
        ]
    )


class VisualAnalysis(BaseModel):
    detected_subjects: List[str] = Field(default_factory=list)
    product_cues: List[str] = Field(default_factory=list)
    color_palette: List[str] = Field(default_factory=list)
    lighting_style: str = "unknown"
    background_style: str = "unknown"
    composition: str = "unknown"
    typography_cues: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    raw: Dict[str, Any] = Field(default_factory=dict)


class SellingMechanism(BaseModel):
    mechanism: str
    buyer_intent: str
    emotional_driver: str
    proof_driver: str
    friction_risk: str
    reason: str


class Scene(BaseModel):
    scene_id: int
    time_range: str
    duration_seconds: float
    goal: str
    visual: str
    camera: str
    motion: str
    lighting: str
    action: str
    voiceover: Optional[str] = None
    on_screen_text: Optional[str] = None
    negative_prompt: str
    provider_prompts: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class Scorecard(BaseModel):
    ctr_score: int = Field(ge=0, le=100)
    attention_score: int = Field(ge=0, le=100)
    trust_score: int = Field(ge=0, le=100)
    conversion_score: int = Field(ge=0, le=100)
    final_score: int = Field(ge=0, le=100)
    verdict: str
    reasons: List[str] = Field(default_factory=list)


class Storyboard(BaseModel):
    storyboard_id: str
    variant: StoryboardVariant
    brief: CampaignBrief
    visual_analysis: VisualAnalysis
    selling_mechanism: SellingMechanism
    scenes: List[Scene]
    scorecard: Scorecard


class StoryboardResponse(BaseModel):
    storyboards: List[Storyboard]
    recommended_variant: StoryboardVariant
    export_ready: bool
