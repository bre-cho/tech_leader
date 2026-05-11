
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

NodeType = Literal[
    "file", "module", "class", "function", "api_route", "worker_task",
    "provider_adapter", "render_contract", "frontend_component", "pipeline_step",
    "production_module"
]

EdgeType = Literal[
    "imports", "calls", "owns", "depends_on", "routes_to", "produces_artifact",
    "uses_contract", "triggers_worker", "renders_ui", "belongs_to_pipeline",
    "next_step", "requires", "fallback_to"
]


class CodeGraphNode(BaseModel):
    id: str
    type: NodeType
    name: str
    path: Optional[str] = None
    layer: str = "unknown"
    domain: str = "unknown"
    summary: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CodeGraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    label: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CodeKnowledgeGraph(BaseModel):
    graph_id: str
    repo_root: str
    generated_at: str
    nodes: List[CodeGraphNode]
    edges: List[CodeGraphEdge]
    domains: Dict[str, List[str]] = Field(default_factory=dict)
    tours: List[Dict[str, Any]] = Field(default_factory=list)


class GraphQueryRequest(BaseModel):
    query: str
    domain_filter: Optional[str] = None
    layer_filter: Optional[str] = None
    limit: int = 20


class ImpactAnalysisRequest(BaseModel):
    changed_paths: List[str]
