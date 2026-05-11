
from fastapi import APIRouter
from .context_core_builder import build_video_factory_context_core
from .context_orchestrator import build_context_pipeline_plan
from .graph_store import load_context_core, save_context_core
from .retriever import query_context, trace_downstream, trace_upstream
from .schemas import ContextQueryRequest, PipelineContextRequest

router = APIRouter(prefix="/api/trustgraph-runtime", tags=["TrustGraph Runtime"])

@router.post("/build-core")
def build_core():
    core = save_context_core(build_video_factory_context_core())
    return {"status": "ok", "context_core_id": core.core_id, "node_count": len(core.nodes), "edge_count": len(core.edges), "path": ".trustgraph-runtime/video-factory-context-core.json"}

@router.get("/core")
def get_core():
    core = load_context_core()
    if core is None:
        return {"status": "missing", "message": "Run POST /api/trustgraph-runtime/build-core first."}
    return core.model_dump()

@router.post("/query")
def query(req: ContextQueryRequest):
    results = query_context(query=req.query, domain_filter=req.domain_filter, node_type_filter=req.node_type_filter, limit=req.limit)
    return {"status": "ok", "results": [item.model_dump() for item in results]}

@router.get("/trace-upstream/{node_id:path}")
def upstream(node_id: str, max_depth: int = 3):
    return trace_upstream(node_id=node_id, max_depth=max_depth)

@router.get("/trace-downstream/{node_id:path}")
def downstream(node_id: str, max_depth: int = 3):
    return trace_downstream(node_id=node_id, max_depth=max_depth)

@router.post("/plan")
def plan(req: PipelineContextRequest):
    return build_context_pipeline_plan(req).model_dump()
