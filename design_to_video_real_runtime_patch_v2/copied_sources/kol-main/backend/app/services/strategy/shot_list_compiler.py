from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.story_beat import BeatType


class Shot(BaseModel):
    shot_index: int
    beat_type: BeatType = BeatType.setup
    duration_seconds: float = 3.0
    camera_movement: str = "static"
    visual_style_note: str = ""
    transition_to_next: str = "cut"


class ShotList(BaseModel):
    topic: str = ""
    shots: list[Shot] = Field(default_factory=list)
