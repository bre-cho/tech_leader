from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

Industry = Literal["beauty","fnb","fashion","saas","education","custom"]
Platform = Literal["tiktok","facebook","instagram","youtube_shorts","multi"]
Format = Literal["9:16","1:1","4:5","16:9"]

class AdsGenerateRequest(BaseModel):
    campaign_id: str = "campaign_auto"
    industry: Industry = "saas"
    platform: Platform = "multi"
    product_name: str
    offer: str | None = None
    audience: str = "người bán hàng online"
    pain_points: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    proof_points: list[str] = Field(default_factory=list)
    cta: str = "Nhận demo miễn phí"
    concepts: int = 3
    hooks_per_concept: int = 5
    formats: list[Format] = Field(default_factory=lambda: ["9:16","1:1"])
    use_video: bool = True
    provider_preference: str | None = None
    character: dict[str, Any] = Field(default_factory=dict)
    style: dict[str, Any] = Field(default_factory=dict)
    motion: dict[str, Any] = Field(default_factory=dict)

class HookCandidate(BaseModel):
    hook_id: str
    hook: str
    industry: str
    formula: str
    intent: str
    emotion: str
    score: float

class CreativeVariant(BaseModel):
    variant_id: str
    concept_name: str
    hook: str
    format: str
    platform: str
    image_prompt: str
    video_prompt: str
    negative_prompt: str
    cta: str
    predicted_ctr_score: float
    predicted_conversion_score: float
    render_payload: dict[str, Any]

class AdsGenerateResponse(BaseModel):
    campaign_id: str
    variants_count: int
    hooks: list[HookCandidate]
    variants: list[CreativeVariant]
    ab_test_plan: dict[str, Any]

class MetricEvent(BaseModel):
    campaign_id: str
    variant_id: str
    impressions: int = 0
    clicks: int = 0
    leads: int = 0
    sales: int = 0
    spend: float = 0.0
    revenue: float = 0.0

class WinnerScore(BaseModel):
    variant_id: str
    ctr: float
    lead_rate: float
    sale_rate: float
    roas: float
    winner_score: float
    decision: Literal["scale","iterate","kill"]
    reason: str
