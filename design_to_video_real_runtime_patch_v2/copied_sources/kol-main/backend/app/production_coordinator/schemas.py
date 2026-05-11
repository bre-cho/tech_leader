
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

CoordinatorMode = Literal["dry_run", "plan_only", "execute"]
StepStatus = Literal["pending", "ready", "skipped", "running", "completed", "failed", "blocked"]


class ProductionInput(BaseModel):
    poster_image_url: Optional[str] = None
    poster_image_path: Optional[str] = None
    campaign_brief: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: int = 30
    aspect_ratio: str = "9:16"
    platform: str = "tiktok_reels_shorts"
    mode: CoordinatorMode = "dry_run"

    enable_multi_angle: bool = True
    enable_higgsfield_seedance2: bool = True
    enable_provider_render: bool = True
    enable_html_render_fallback: bool = True
    enable_audio: bool = True
    enable_avatar: bool = False
    enable_drama: bool = True
    enable_smart_subtitle: bool = True
    enable_final_assembly: bool = True
    enable_analytics_feedback: bool = False

    provider_priority: List[str] = Field(default_factory=lambda: ["seedance2", "kling", "runway", "veo"])


class ProductionStep(BaseModel):
    step_id: str
    name: str
    domain: str
    order: int
    required: bool = True
    enabled: bool = True
    status: StepStatus = "pending"
    input_keys: List[str] = Field(default_factory=list)
    output_keys: List[str] = Field(default_factory=list)
    module_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    api_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    hard_rules: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class ProductionPlan(BaseModel):
    plan_id: str
    graph_id: Optional[str] = None
    input_summary: Dict[str, Any]
    steps: List[ProductionStep]
    execution_order: List[str]
    missing_required_domains: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    render_package_contract: Dict[str, Any] = Field(default_factory=dict)


class StepRunResult(BaseModel):
    step_id: str
    status: StepStatus
    message: str
    outputs: Dict[str, Any] = Field(default_factory=dict)


class ProductionRunResult(BaseModel):
    plan_id: str
    mode: CoordinatorMode
    status: StepStatus
    step_results: List[StepRunResult]
    final_contract: Dict[str, Any] = Field(default_factory=dict)
