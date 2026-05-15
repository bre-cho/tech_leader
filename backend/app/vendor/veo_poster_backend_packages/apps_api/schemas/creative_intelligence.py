from typing import Any

from pydantic import BaseModel, Field


class CreativeSessionCreate(BaseModel):
    brand_id: str | None = None
    industry: str
    product: str
    goal: str = "premium_conversion"
    platform: str = "instagram"
    audience: str = "mass_market"
    perception_targets: list[str] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)


class CreativeSessionOut(CreativeSessionCreate):
    id: str


class CreativePlanOut(BaseModel):
    session_id: str
    creative_direction: dict[str, Any]
    selected_skills: list[dict[str, Any]]
    design_system: dict[str, Any]
    composition_plan: dict[str, Any]
    typography_plan: dict[str, Any]
    visual_fx_plan: dict[str, Any]
    prompt_stack: dict[str, Any]
    graph: dict[str, Any]


class ScoreRequest(BaseModel):
    creative_plan: dict[str, Any] | None = None


class ScoreOut(BaseModel):
    ctr_score: float
    luxury_score: float
    readability_score: float
    brand_recall_score: float
    emotional_score: float
    analysis: dict[str, Any]


class RenderJobCreate(BaseModel):
    session_id: str | None = None
    prompt: str
    provider: str = "mock"


class RenderJobOut(BaseModel):
    id: str
    session_id: str | None = None
    status: str
    provider: str
    result: dict[str, Any] | None = None
    error: str | None = None


class BrandDNAUpsertRequest(BaseModel):
    dna: dict[str, Any] = Field(default_factory=dict)


class BrandDNAOut(BaseModel):
    brand_id: str
    dna: dict[str, Any] | None = None
