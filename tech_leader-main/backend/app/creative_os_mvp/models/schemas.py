from typing import Any, Literal
from pydantic import BaseModel, Field

class BrandContext(BaseModel):
    brand_name: str = ""
    industry: str = "beauty"
    product_name: str = ""
    product_type: str = ""
    audience: str = ""
    channel: str = "TikTok ads"
    objective: str = "conversion"
    brand_dna: dict[str, Any] = Field(default_factory=dict)

class CreativeRequest(BaseModel):
    request_id: str | None = None
    brand: BrandContext
    brief: str
    campaign_type: str = "commercial_visual"
    aspect_ratio: str = "4:5"
    output_targets: list[str] = Field(default_factory=lambda:["social", "poster", "storyboard"])
    quality: Literal["draft", "premium", "hero"] = "premium"
    enable_hidream: bool = True
    save_memory: bool = True

class RuntimeStage(BaseModel):
    name: str
    status: Literal["passed","blocked","warning"]
    details: dict[str, Any] = Field(default_factory=dict)

class CommercialReasoning(BaseModel):
    attention_route: list[dict[str, Any]]
    typography: dict[str, Any]
    product_hero: dict[str, Any]
    environment_reaction: dict[str, Any]
    psychology: dict[str, Any]
    billboard_print: dict[str, Any]
    category: dict[str, Any]
    score_breakdown: dict[str, float]
    total_score: float

class Artifact(BaseModel):
    artifact_id: str
    artifact_type: str
    path: str
    url: str | None = None
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class CreativeRunResponse(BaseModel):
    run_id: str
    status: Literal["completed","blocked","failed"]
    stages: list[RuntimeStage]
    reasoning: CommercialReasoning | None = None
    prompt: str | None = None
    negative_prompt: str | None = None
    artifacts: list[Artifact] = Field(default_factory=list)
    storyboard: list[dict[str, Any]] = Field(default_factory=list)
    memory_update: dict[str, Any] = Field(default_factory=dict)
    promotion: dict[str, Any] = Field(default_factory=dict)
