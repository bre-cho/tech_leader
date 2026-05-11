from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LineageSchema(BaseModel):
    step: str
    parent_step_id: Optional[str] = None
    artifact_id: Optional[str] = None


class StandardApiResponse(BaseModel):
    ok: bool = True
    trace_id: str
    project_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    lineage: LineageSchema


class DesignGenerateRequest(BaseModel):
    industry: str
    product: str
    target_customer: Optional[str] = None
    channel: str = "Facebook"
    goal: str = "sales"
    pain_point: Optional[str] = None
    selling_angle: Optional[str] = None


class DesignSelectRequest(BaseModel):
    project_id: str
    trace_id: str
    selected_variant_id: Optional[str] = None
    selected_variant: Dict[str, Any]
    channel: str = "Facebook"
    product: str
    industry: str
    product_type: str = "physical"
    purchase_confirmed: bool = False


class RenderProjectRequest(BaseModel):
    project_id: str
    trace_id: str
    provider: str = "adapter"
    storyboard: List[Dict[str, Any]] = Field(default_factory=list)
