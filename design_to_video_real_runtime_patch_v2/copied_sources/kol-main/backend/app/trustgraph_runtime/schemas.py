
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

ContextNodeType = Literal["module","pipeline_step","data_contract","artifact","policy","evidence","fallback","quality_gate","agent_tool"]
ContextEdgeType = Literal["requires","produces","consumes","validates","fallback_to","controlled_by","evidenced_by","next_step","tool_for","blocks_if_missing"]

class ProvenanceRef(BaseModel):
    source_type: str = "code"
    source_path: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float = 1.0
    note: str = ""

class ContextGraphNode(BaseModel):
    id: str
    type: ContextNodeType
    name: str
    domain: str
    summary: str = ""
    payload_schema: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: List[ProvenanceRef] = Field(default_factory=list)

class ContextGraphEdge(BaseModel):
    source: str
    target: str
    type: ContextEdgeType
    label: str = ""
    policy: Dict[str, Any] = Field(default_factory=dict)
    provenance: List[ProvenanceRef] = Field(default_factory=list)

class ContextCore(BaseModel):
    core_id: str
    version: str = "v1"
    name: str
    description: str = ""
    nodes: List[ContextGraphNode]
    edges: List[ContextGraphEdge]
    retrieval_policies: Dict[str, Any] = Field(default_factory=dict)
    promotion_policy: Dict[str, Any] = Field(default_factory=dict)

class PipelineContextRequest(BaseModel):
    poster_image_url: Optional[str] = None
    poster_image_path: Optional[str] = None
    campaign_brief: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: int = 30
    aspect_ratio: str = "9:16"
    platform: str = "tiktok_reels_shorts"
    objective: str = "produce_final_video"
    provider_priority: List[str] = Field(default_factory=lambda: ["seedance2", "kling", "runway", "veo"])
    execution_mode: Literal["plan", "dry_run", "execute_guarded"] = "plan"

class ContextQueryRequest(BaseModel):
    query: str
    domain_filter: Optional[str] = None
    node_type_filter: Optional[ContextNodeType] = None
    limit: int = 20

class PipelineDecision(BaseModel):
    decision_id: str
    step_id: str
    selected_module: Optional[str] = None
    reason: str
    required_inputs: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    fallback_options: List[str] = Field(default_factory=list)
    blocking_policies: List[str] = Field(default_factory=list)
    evidence: List[ProvenanceRef] = Field(default_factory=list)

class ContextPipelinePlan(BaseModel):
    plan_id: str
    context_core_id: str
    status: Literal["ready", "blocked", "partial"]
    decisions: List[PipelineDecision]
    missing_inputs: List[str] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)
    final_contract_requirements: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# ── P1 contract schemas ───────────────────────────────────────────────────────

class MemoryRef(BaseModel):
    memory_id: str
    memory_type: str = "organizational"
    scope: Optional[str] = None
    source_agent: Optional[str] = None
    created_at: Optional[str] = None
    note: str = ""


class AgentAssignment(BaseModel):
    agent_id: str
    module_id: str
    role: str
    assigned_at: Optional[str] = None
    status: Literal["assigned", "running", "completed", "failed"] = "assigned"
    memory_refs: List[MemoryRef] = Field(default_factory=list)


class ArtifactLineageRef(BaseModel):
    artifact_id: str
    artifact_type: str
    context_run_id: Optional[str] = None
    decision_id: Optional[str] = None
    graph_node_id: Optional[str] = None
    parent_artifact_id: Optional[str] = None
    provenance: List[ProvenanceRef] = Field(default_factory=list)


class ReplayManifestRef(BaseModel):
    manifest_id: str
    context_run_id: str
    runtime_version: str
    deterministic_hash: Optional[str] = None
    artifact_ids: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    verified: bool = False


class ContextRun(BaseModel):
    run_id: str
    plan_id: str
    context_core_id: str
    status: Literal["pending", "running", "completed", "blocked", "failed"] = "pending"
    decisions: List[PipelineDecision] = Field(default_factory=list)
    agent_assignments: List[AgentAssignment] = Field(default_factory=list)
    missing_inputs: List[str] = Field(default_factory=list)
    artifact_lineage: List[ArtifactLineageRef] = Field(default_factory=list)
    replay_manifest: Optional[ReplayManifestRef] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

