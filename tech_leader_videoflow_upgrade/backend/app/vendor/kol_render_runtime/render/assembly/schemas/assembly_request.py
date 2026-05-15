from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssemblyRequest(BaseModel):
    project_id: str
    episode_id: str
    assembly_plan: dict[str, Any] = Field(default_factory=dict)
