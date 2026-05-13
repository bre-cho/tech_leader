from typing import Any, Literal
from pydantic import BaseModel, Field

class DesignStudioRequest(BaseModel):
    industry: str = Field(..., min_length=2)
    product: str = Field(..., min_length=2)
    audience: str = Field(..., min_length=2)
    channel: str = Field(..., min_length=2)
    goal: str = Field(..., min_length=2)
    brand_name: str = ""
    tone: str = "premium, trustworthy, conversion-focused"
    budget_tier: Literal["low", "mid", "premium"] = "mid"
    language: str = "vi"
    dry_run: bool = False

class ScoreCard(BaseModel):
    attention_score: int
    trust_score: int
    conversion_score: int
    brand_fit_score: int
    upsell_video_potential_score: int
    video_upsell_ready: bool
    rationale: str

class ImageConcept(BaseModel):
    concept_id: str
    headline: str
    cta: str
    visual_type: str
    layout_direction: str
    prompt: str
    negative_prompt: str | None = None
    mock_image_url: str | None = None
    score: ScoreCard | None = None
    provider_contract: dict[str, Any] | None = None
    selling_mechanism: dict[str, Any] | None = None

class OperatingLawTrace(BaseModel):
    target_define: bool
    research: bool
    plan: bool
    execute: bool
    verify: bool
    distill_to_skill: bool
    memory_update: bool
    winner_dna_update: bool

class DesignStudioResponse(BaseModel):
    workflow_id: str
    dry_run: bool = False
    promotion_mode: Literal["REAL", "DRY_RUN"] = "REAL"
    operating_law: str
    law_trace: OperatingLawTrace
    technical_lead_plan: dict[str, Any]
    capability_route: list[dict[str, Any]]
    recalled_winner_dna: list[dict[str, Any]]
    business_diagnosis: dict[str, Any]
    image_concepts: list[ImageConcept]
    best_concept: ImageConcept
    upsell_analysis: dict[str, Any]
    video_concept_preview: dict[str, Any]
    storyboard: list[dict[str, Any]]
    offer_packages: list[dict[str, Any]]
    skill_distillation: dict[str, Any]
    context_graph_update: dict[str, Any] | None = None
    memory_update: dict[str, Any]
    verification: dict[str, Any]
    promotion_gate: dict[str, Any]
