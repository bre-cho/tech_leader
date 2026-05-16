from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator

class StoryboardPlanRequest(BaseModel):
    image_source: Literal["upload", "generated"]
    image_url: str
    target_video_duration: float = Field(gt=0)
    provider: str
    planned_batch_size: Optional[int] = None
    max_concurrent_render: int = 1

    @field_validator("max_concurrent_render")
    @classmethod
    def force_safe_concurrency(cls, value: int) -> int:
        return 1

class StoryboardScene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    index: int
    title: str
    camera: str
    motion: str
    subtitle: str
    provider: str
    duration: float
    continuity_key: str
    prompt: Optional[str] = None
    aspect_ratio: Optional[str] = None
    prompt_preset: Optional[str] = None
    status: str = "planned"

class RenderBatch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    batch_index: int
    scene_indexes: List[int]
    planned_batch_size: int
    max_concurrent_render: int = 1
    execution_mode: str = "sequential"
    status: str = "queued"

class StoryboardPlan(BaseModel):
    project_id: str
    image_source: Literal["upload", "generated"]
    image_url: str
    target_video_duration: float
    provider: str
    recommended_duration_per_scene: float
    scene_count: int
    scene_duration: float
    planned_batch_size: int
    max_concurrent_render: int = 1
    total_batches: int
    execution_mode: str = "sequential"
    scenes: List[StoryboardScene]
    batches: List[RenderBatch]

class RuntimeEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    message: str
    payload: Dict[str, Any] = Field(default_factory=dict)
