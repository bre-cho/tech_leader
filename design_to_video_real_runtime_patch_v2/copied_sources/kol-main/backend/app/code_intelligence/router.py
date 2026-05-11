
from __future__ import annotations

from fastapi import APIRouter

from .schemas import GraphQueryRequest, ImpactAnalysisRequest
from .service import build_and_save_graph, impact_for_paths, load_graph, query_graph

router = APIRouter(prefix="/api/code-intelligence", tags=["Code Intelligence"])


@router.post("/build")
def build_graph(repo_root: str = "."):
    graph = build_and_save_graph(repo_root=repo_root)
    return {
        "status": "ok",
        "graph_id": graph.graph_id,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "domain_count": len(graph.domains),
        "path": ".code-intelligence/knowledge-graph.json",
    }


@router.get("/graph")
def get_graph():
    graph = load_graph()
    if graph is None:
        return {"status": "missing", "message": "Run POST /api/code-intelligence/build first."}
    return graph.model_dump()


@router.post("/query")
def query(req: GraphQueryRequest):
    return {
        "status": "ok",
        "results": query_graph(
            query=req.query,
            domain_filter=req.domain_filter,
            layer_filter=req.layer_filter,
            limit=req.limit,
        ),
    }


@router.post("/impact")
def impact(req: ImpactAnalysisRequest):
    return impact_for_paths(req.changed_paths)
