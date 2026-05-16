from typing import Dict, List
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class FashionRuntimeRequest(BaseModel):
    brief: str
    target_duration: float = Field(default=60, gt=0)
    provider: str = "kling"
    planned_batch_size: int = 6
    max_concurrent_render: int = 1
    channel: str = "tiktok_reels_shorts"
    language: str = "vi"

    @field_validator("max_concurrent_render")
    @classmethod
    def force_sequential(cls, value: int) -> int:
        return 1


class VisualDNA(BaseModel):
    archetype: str
    palette: List[str]
    material_language: List[str]
    lighting_language: str
    camera_language: List[str]
    hair_signature: str
    luxury_signals: List[str]
    motion_signals: List[str]
    commerce_angle: str
    scores: Dict[str, float]


class EmotionalPerceptionGraph(BaseModel):
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]
    dominant_emotion: str
    virality_hook: str


class CharacterContinuityLock(BaseModel):
    face_identity: str
    hair_identity: str
    outfit_rules: List[str]
    makeup_rules: List[str]
    pose_rules: List[str]
    drift_guards: List[str]


class FashionMotionPlan(BaseModel):
    motion_style: str
    camera_rhythm: List[str]
    pose_sequence: List[str]
    hair_motion: str
    cloth_motion: str


class BeautyCommercePlan(BaseModel):
    product_positioning: str
    audience_desire: str
    trust_triggers: List[str]
    conversion_triggers: List[str]
    content_angle: str


class FashionStoryboardScene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scene_index: int
    title: str
    visual_prompt: str
    camera: str
    motion: str
    duration: float
    provider: str
    continuity_notes: List[str]


class SequentialRenderStep(BaseModel):
    batch_index: int
    scene_index: int
    status: str = "queued"
    max_concurrent_render: int = 1
    execution_mode: str = "sequential"


class FashionRuntimeResponse(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid4()))
    brief: str
    visual_dna: VisualDNA
    emotional_graph: EmotionalPerceptionGraph
    continuity_lock: CharacterContinuityLock
    fashion_motion: FashionMotionPlan
    beauty_commerce: BeautyCommercePlan
    storyboard: List[FashionStoryboardScene]
    sequential_render_plan: List[SequentialRenderStep]
    winner_dna_memory: Dict
