
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional


ProviderName = Literal["veo", "runway", "kling", "seedance2", "html_motion"]


class MultiAngleRequest(BaseModel):
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    subject_type: str = Field(default="product", description="car, person, fashion, product, food, real_estate, news_visual")
    brand: Optional[str] = None
    product_name: Optional[str] = None
    platform: str = "tiktok_reels_shorts"
    aspect_ratio: str = "9:16"
    duration_seconds: int = 30
    provider_priority: List[ProviderName] = Field(default_factory=lambda: ["seedance2", "kling", "runway", "veo"])
    style: str = "cinematic commercial, premium, realistic"
    generate_reference_sheet: bool = True
    include_detail_shots: bool = True
    include_dynamic_shots: bool = True
    include_lifestyle_shots: bool = True


class AngleSpec(BaseModel):
    angle_id: str
    label: str
    group: str
    shot_size: str
    camera_angle: str
    camera_motion: str
    lens: str
    duration: float
    priority: int
    continuity_notes: List[str] = Field(default_factory=list)
    prompt_intent: str


class MultiAngleScene(BaseModel):
    scene_id: str
    time_range: str
    goal: str
    source_angle: AngleSpec
    visual_prompt: str
    video_prompt: str
    provider_payloads: List[Dict[str, Any]]
    quality_rules: List[str]


class MultiAngleStoryboard(BaseModel):
    storyboard_id: str
    input_image: Optional[str]
    subject_type: str
    brand: Optional[str]
    product_name: Optional[str]
    aspect_ratio: str
    duration_seconds: int
    angle_library: List[AngleSpec]
    scenes: List[MultiAngleScene]
    reference_sheet_plan: Dict[str, Any]
    render_package_patch: Dict[str, Any]
