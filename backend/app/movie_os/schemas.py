from typing import Dict, List
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class MovieDirectorRequest(BaseModel):
    prompt: str
    target_duration: float = Field(default=60, gt=0)
    provider: str = "kling"
    planned_batch_size: int = 6
    max_concurrent_render: int = 1

    @field_validator("max_concurrent_render")
    @classmethod
    def force_safe_concurrency(cls, value: int) -> int:
        return 1


class MovieScene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scene_index: int
    title: str
    visual_prompt: str
    camera: str
    motion: str
    lens: str
    lighting: str
    duration: float
    continuity_notes: List[str]
    provider: str


class MovieDirectorResponse(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str
    mood_profile: Dict
    character_bible: Dict
    storyboard: List[MovieScene]
    rhythm_timeline: Dict
    editor_plan: Dict
    assembly_plan: Dict
    sequential_render_policy: Dict
