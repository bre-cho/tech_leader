from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OperatingStage(str, Enum):
    target_define = "TARGET_DEFINE"
    research = "RESEARCH"
    plan = "PLAN"
    execute = "EXECUTE"
    verify = "VERIFY"
    distill_to_skill = "DISTILL_TO_SKILL"
    memory_update = "MEMORY_UPDATE"
    winner_dna_update = "WINNER_DNA_UPDATE"


class BusinessInput(BaseModel):
    brand_name: str
    industry: str
    product_name: str
    product_type: str
    audience: str
    goal: str = "conversion"
    channel: str = "tiktok"
    offer: Optional[str] = None
    brand_assets: List[str] = Field(default_factory=list)
    reference_notes: Optional[str] = None


class CreativeRunRequest(BaseModel):
    business: BusinessInput
    provider: str = "mock"
    export_targets: List[str] = Field(default_factory=lambda: ["poster", "tiktok", "landing"])
    save_memory: bool = True


class CanvasRegion(BaseModel):
    name: str
    purpose: str
    priority: int
    x: float
    y: float
    width: float
    height: float
    rules: List[str]


class DesignSystem(BaseModel):
    colors: List[str]
    typography: List[str]
    spacing: Dict[str, Any]
    visual_language: List[str]
    composition_rules: List[str]
    brand_personality: Dict[str, Any]
    motion_style: Dict[str, Any]
    trust_style: Dict[str, Any]
    cta_style: Dict[str, Any]


class GraphEdge(BaseModel):
    source: str
    relation: str
    target: str
    weight: float
    evidence: str


class AgentResult(BaseModel):
    agent: str
    status: str
    output: Dict[str, Any]


class VerificationReport(BaseModel):
    passed: bool
    score: float
    checks: Dict[str, bool]
    issues: List[str] = Field(default_factory=list)


class CreativeRunResponse(BaseModel):
    run_id: str
    stages_completed: List[OperatingStage]
    operating_law_passed: bool
    design_system: DesignSystem
    canvas_regions: List[CanvasRegion]
    creative_graph_edges: List[GraphEdge]
    agent_results: List[AgentResult]
    final_prompt: str
    storyboard: List[Dict[str, Any]]
    verification: VerificationReport
    promotion_status: str
    memory_update: Dict[str, Any]
    winner_dna: Dict[str, Any]
