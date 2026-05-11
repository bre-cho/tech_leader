from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

EmotionIntent = Literal["luxury", "tension", "trust", "power", "viral_energy", "intimacy", "freshness", "mystery", "authority"]
ProviderName = Literal["veo", "runway", "kling", "seedance2", "html_motion"]

class CinematicRequest(BaseModel):
    poster_image_url: Optional[str] = None
    campaign_brief: Dict[str, Any] = Field(default_factory=dict)
    subject_type: str = "product"
    platform: str = "tiktok_reels_shorts"
    aspect_ratio: str = "9:16"
    duration_seconds: int = 30
    emotion_intent: EmotionIntent = "luxury"
    providers: List[ProviderName] = Field(default_factory=lambda: ["seedance2", "kling", "runway", "veo"])
    include_multi_angle: bool = True
    include_safe_zone: bool = True
    include_viral_hook: bool = True

class ShotTechnique(BaseModel):
    technique_id: str
    family: str
    name: str
    shot_type: str
    lens: str
    camera_motion: str
    emotional_effect: str
    best_for: List[str] = Field(default_factory=list)
    provider_notes: Dict[str, str] = Field(default_factory=dict)
    prompt_fragment: str

class CinematicScenePlan(BaseModel):
    scene_id: str
    time_range: str
    goal: str
    selected_technique: ShotTechnique
    composition: str
    lighting: str
    motion: str
    safe_zone: Dict[str, Any] = Field(default_factory=dict)
    cinematic_prompt: str
    provider_payloads: List[Dict[str, Any]] = Field(default_factory=list)
    quality_rules: List[str] = Field(default_factory=list)

class CinematicStoryboard(BaseModel):
    storyboard_id: str
    source_image: Optional[str] = None
    campaign_brief: Dict[str, Any] = Field(default_factory=dict)
    emotion_intent: EmotionIntent
    aspect_ratio: str
    duration_seconds: int
    scenes: List[CinematicScenePlan]
    cinematic_scorecard: Dict[str, Any] = Field(default_factory=dict)
    render_package_patch: Dict[str, Any] = Field(default_factory=dict)
