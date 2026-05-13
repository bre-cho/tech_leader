from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class InfrastructureRequest(BaseModel):
    business_goal: str
    industry: str
    product_or_service: str
    audience: str
    platform: str = "tiktok_ads"
    campaign_type: str = "commercial_visual"
    brand_context: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    requested_outputs: List[str] = Field(default_factory=lambda: ["poster", "storyboard", "video_concept"])

class InfrastructureResponse(BaseModel):
    request_id: str
    operating_law_status: Dict[str, Any]
    technical_lead_plan: Dict[str, Any]
    workflow_graph: Dict[str, Any]
    execution_result: Dict[str, Any]
    verification: Dict[str, Any]
    promotion_gate: Dict[str, Any]
    memory_update: Dict[str, Any]
    winner_dna: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
