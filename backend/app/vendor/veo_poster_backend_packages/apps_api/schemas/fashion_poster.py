from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PosterStyle(str, Enum):
    y2k = "y2k"
    luxury = "luxury"
    dark_feminine = "dark_feminine"
    vogue = "vogue"
    viral = "viral"


class PosterGoal(str, Enum):
    attention = "attention"
    luxury = "luxury"
    editorial = "editorial"
    conversion = "conversion"
    viral = "viral"
    branding = "branding"


class RenderProvider(str, Enum):
    mock = "mock"
    adobe = "adobe"
    canva = "canva"
    auto = "auto"


class FashionPosterInput(BaseModel):
    identity: str = Field(..., examples=["modern it girl"])
    style: PosterStyle = PosterStyle.dark_feminine
    goal: PosterGoal = PosterGoal.editorial
    target: str = "gen z women"
    palette: list[str] | None = None
    hero_images: list[str] = Field(default_factory=list, description="Image URLs or asset IDs")
    secondary_images: list[str] = Field(default_factory=list)
    headline: str | None = None
    subtitle: str | None = None
    language: str = "vi"
    variant_count: int = Field(default=6, ge=1, le=30)
    provider: RenderProvider = RenderProvider.mock
    render_winner: bool = True


class Zone(BaseModel):
    id: str
    type: str
    x: float
    y: float
    w: float
    h: float
    z: int
    rotation: float = 0
    notes: str = ""


class TypographyPlan(BaseModel):
    h1: str
    h2: str
    h3: list[str]
    h4: list[str]
    font_logic: dict[str, str]
    hierarchy_notes: list[str]


class ScoreCard(BaseModel):
    attention: int
    luxury: int
    editorial: int
    readability: int
    viral: int
    brand_identity: int
    total: int


class FashionPosterVariant(BaseModel):
    variant_id: str
    style_route: str
    prompt: str
    negative_prompt: str
    layout: list[Zone]
    typography: TypographyPlan
    texture_stack: list[str]
    scores: ScoreCard
    dna: dict[str, Any]


class RenderArtifact(BaseModel):
    artifact_id: str
    artifact_type: str
    mime_type: str
    url: str
    provider_used: str
    prompt_used: str
    adobe_asset_id: str | None = None
    canva_design_id: str | None = None
    image_url: str | None = None
    export_url: str | None = None
    metadata: dict[str, Any] | None = None


class FashionPosterResponse(BaseModel):
    winner: FashionPosterVariant
    variants: list[FashionPosterVariant]
    winner_render: RenderArtifact | None = None
    provider_requested: str
    render_error: str | None = None
    production_notes: list[str]
