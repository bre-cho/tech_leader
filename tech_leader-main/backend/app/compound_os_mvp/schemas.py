from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BrandCreate(BaseModel):
    name: str
    industry: str
    identity: Dict[str, Any] = Field(default_factory=dict)

class CampaignCreate(BaseModel):
    brand_name: str
    industry: str
    campaign_name: str
    product_name: str
    product_type: str
    audience: str
    goal: str = "conversion"
    channel: str = "tiktok"
    offer: Optional[str] = None
    variants: int = 3

class WorkflowRunRequest(CampaignCreate):
    save_memory: bool = True

class MetricIngest(BaseModel):
    campaign_id: int
    variant_id: int
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0
    watch_time_rate: float = 0

class GraphEdgeOut(BaseModel):
    source: str
    relation: str
    target: str
    weight: float
    evidence: str
    observations: int

class CreativeVariantOut(BaseModel):
    id: int
    name: str
    layout: str
    hook: str
    typography: str
    visual_style: str
    offer: str
    score: float
    prompt: str
    storyboard: List[Dict[str, Any]]

class WorkflowRunResponse(BaseModel):
    run_id: str
    status: str
    operating_law_passed: bool
    campaign_id: int
    brand_memory: Dict[str, Any]
    creative_graph: List[GraphEdgeOut]
    variants: List[CreativeVariantOut]
    workforce_report: List[Dict[str, Any]]
    optimization_report: Dict[str, Any]
    winner_dna: Dict[str, Any]
