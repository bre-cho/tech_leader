from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TimelineRequest(BaseModel):
    project_id: str
    episode_id: str
    render_scenes: list[dict[str, Any]] = Field(default_factory=list)
