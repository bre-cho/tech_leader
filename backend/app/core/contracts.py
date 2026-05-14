from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStage(str, Enum):
    target_define = "TARGET_DEFINE"
    research = "RESEARCH"
    plan = "PLAN"
    execute = "EXECUTE"
    verify = "VERIFY"
    distill_to_skill = "DISTILL_TO_SKILL"
    memory_update = "MEMORY_UPDATE"
    winner_dna_update = "WINNER_DNA_UPDATE"


class Channel(str, Enum):
    facebook = "facebook"
    tiktok = "tiktok"
    shopee = "shopee"
    landing_page = "landing_page"
    billboard = "billboard"
    ecommerce = "ecommerce"
    instagram = "instagram"
    youtube = "youtube"


class CreativeGoal(str, Enum):
    conversion = "conversion"
    awareness = "awareness"
    product_launch = "product_launch"
    promotion = "promotion"
    trust = "trust"
    premium_branding = "premium_branding"


class BusinessInput(BaseModel):
    brand_name: str = Field(..., min_length=1)
    industry: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1)
    product_type: str = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    channel: Channel = Channel.tiktok
    goal: CreativeGoal = CreativeGoal.conversion
    offer: Optional[str] = None
    brand_tone: Optional[str] = "premium, trustworthy, modern"
    constraints: List[str] = Field(default_factory=list)


class CreativeOSRequest(BaseModel):
    input: BusinessInput
    workflow_id: str = "commercial_campaign_v1"
    provider: str = "hf_inference"
    generate_image: bool = False
    export_targets: List[str] = Field(default_factory=lambda: ["social", "landing_page"])
    save_memory: bool = True


class VisualDecision(BaseModel):
    attention_route: List[str]
    dopamine_triggers: List[str]
    trust_triggers: List[str]
    conversion_triggers: List[str]
    typography_plan: Dict[str, Any]
    product_hero_plan: Dict[str, Any]
    environment_reaction_plan: Dict[str, Any]
    commercial_psychology: Dict[str, Any]
    print_export_plan: Dict[str, Any]


class AgentOutput(BaseModel):
    agent_name: str
    status: str
    data: Dict[str, Any]


class ArtifactContract(BaseModel):
    artifact_id: str
    artifact_type: str
    path_or_url: str
    mime_type: str
    checksum_sha256: str
    created_by: str
    source_workflow_id: str
    replay_payload_hash: str


class VerificationReport(BaseModel):
    passed: bool
    score: float
    checks: Dict[str, bool]
    issues: List[str] = Field(default_factory=list)


class CreativeOSResponse(BaseModel):
    run_id: str
    operating_law_passed: bool
    stages_completed: List[WorkflowStage]
    decisions: VisualDecision
    prompt: str
    negative_prompt: str
    agent_outputs: List[AgentOutput]
    verification: VerificationReport
    promotion_status: str
    winner_dna_candidate: Dict[str, Any]
    artifacts: List[ArtifactContract]
    storyboard: List[Dict[str, Any]]
    memory_update: Dict[str, Any]
