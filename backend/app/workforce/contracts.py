from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class BusinessBrief(BaseModel):
    brand_name: str
    industry: str
    product_name: str
    product_type: str
    target_audience: str
    campaign_goal: str = "conversion"
    channel: str = "tiktok"
    offer: Optional[str] = None
    brand_tone: str = "premium, trustworthy, modern"
    constraints: List[str] = Field(default_factory=list)


class WorkforceContext(BaseModel):
    brief: BusinessBrief
    memory: Dict[str, Any] = Field(default_factory=dict)
    design_system: Dict[str, Any] = Field(default_factory=dict)
    creative_graph: List[Dict[str, Any]] = Field(default_factory=list)
    canvas_regions: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: Dict[str, Any] = Field(default_factory=dict)
    risks: List[str] = Field(default_factory=list)
    qa_checks: Dict[str, bool] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus
    confidence: float = 0.0
    output: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class WorkforceRunRequest(BaseModel):
    brief: BusinessBrief
    save_memory: bool = True
    dry_run: bool = False


class WorkforceRunResponse(BaseModel):
    run_id: str
    status: str
    dry_run: bool = False
    law_trace: Dict[str, bool] = Field(default_factory=dict)
    context: WorkforceContext
    agent_results: List[AgentResult]
    final_prompt: str
    negative_prompt: str
    storyboard: List[Dict[str, Any]]
    artifact: Dict[str, Any] = Field(default_factory=dict)
    verification: Dict[str, Any] = Field(default_factory=dict)
    verification_score: float
    promotion_status: str
    promotion_gate: Dict[str, Any] = Field(default_factory=dict)
    memory_update: Dict[str, Any] = Field(default_factory=dict)
    context_graph_update: Dict[str, Any] = Field(default_factory=dict)
    winner_dna: Dict[str, Any]
