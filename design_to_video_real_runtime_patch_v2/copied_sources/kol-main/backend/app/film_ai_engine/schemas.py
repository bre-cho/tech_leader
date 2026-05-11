from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProjectBible(BaseModel):
    project_title: str = Field(default="AUTO POSTER CINEMATIC CAMPAIGN")
    core_premise: str = Field(default="Transform a poster or campaign brief into a cinematic micro-saga video.")
    pillars: List[str] = Field(default_factory=lambda: ["emotion-first", "visual tactility", "sound-first AEO"])
    narrator_persona: str = "The Brand Skald"
    voice_direction: str = "slow, intimate, cinematic, spacious pacing"
    visual_style_base: str = "cinematic commercial, photorealistic, tactile texture, premium lighting"
    motion_style: str = "slow controlled camera, micro-movements, atmosphere, no chaotic motion"
    palette: List[str] = Field(default_factory=lambda: ["brand primary", "brand secondary", "shadow", "highlight", "accent"])
    aeo_philosophy: str = "Sound-first. Music supports the world and never overwhelms voice or tactile foley."
    soundscape_layers: Dict[str, str] = Field(default_factory=lambda: {
        "environment": "ambient room/wind/city/nature texture",
        "foley": "fabric, product touch, breath, steps, hand movement",
        "music": "minimal cinematic bed, restrained pulse"
    })
    negative_guardrails: List[str] = Field(default_factory=lambda: [
        "no distorted anatomy", "no unreadable text", "no watermark", "no fast chaotic movement", "no style mismatch"
    ])

class ShotBlock(BaseModel):
    shot_id: str
    sequence: str
    beat: str
    time_range: str
    camera: str
    action: str
    sfx: str
    narrator_vo: str
    scale: str = "medium"
    lighting: str = "cinematic"
    micro_movement: str = "subtle motion"

class DirectorPassOutput(BaseModel):
    total_shots: int
    assets: List[Dict[str, Any]]
    image_prompts: List[Dict[str, Any]]
    video_prompts: List[Dict[str, Any]]
    verification: Dict[str, Any]

class AEOPlan(BaseModel):
    voice_prompt: str
    narration_text: str
    environment_layer: str
    foley_layer: str
    music_layer: str
    mix_policy: Dict[str, Any]
