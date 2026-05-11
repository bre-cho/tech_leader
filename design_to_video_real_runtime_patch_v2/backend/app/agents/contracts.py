from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class AgentName(str, Enum):
    BUSINESS_DIAGNOSIS = "business_diagnosis"
    INDUSTRY_ADAPTATION = "industry_adaptation"
    IMAGE_DESIGN = "image_design"
    IMAGE_QA = "image_qa"
    UPSELL_OPPORTUNITY = "upsell_opportunity"
    VIDEO_CONCEPT = "video_concept"
    STORYBOARD = "storyboard"
    OFFER = "offer"
    CRM_FOLLOWUP = "crm_followup"
    ANALYTICS = "analytics"
    MEMORY_UPDATE = "memory_update"
    TECHLEAD_AUDIT = "techlead_audit"


class Lineage(BaseModel):
    step: str
    parent_step_id: Optional[str] = None
    artifact_id: Optional[str] = None


class AgentEnvelope(BaseModel):
    agent_name: AgentName
    project_id: str
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    decision_reason: str = ""
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    warnings: List[str] = Field(default_factory=list)
    lineage: Lineage


class StandardResponse(BaseModel):
    ok: bool = True
    trace_id: str
    project_id: str
    data: Dict[str, Any]
    warnings: List[str] = Field(default_factory=list)
    lineage: Lineage
