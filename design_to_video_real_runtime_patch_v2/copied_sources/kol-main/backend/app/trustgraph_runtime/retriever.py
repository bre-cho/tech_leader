
from .graph_store import load_context_core

def query_context(query: str, domain_filter: str | None = None, node_type_filter: str | None = None, limit: int = 20):
    core = load_context_core()
    if not core:
        return []
    q = query.lower().strip()
    results = []
    for node in core.nodes:
        if domain_filter and node.domain != domain_filter:
            continue
        if node_type_filter and node.type != node_type_filter:
            continue
        hay = f"{node.name} {node.domain} {node.type} {node.summary}".lower()
        if q in hay or any(token in hay for token in q.split()):
            results.append(node)
            if len(results) >= limit:
                break
    return results

def trace_upstream(node_id: str, max_depth: int = 3):
    core = load_context_core()
    if not core:
        return {"status": "missing_context_core", "trace": []}
    trace, frontier = [], {node_id}
    for _ in range(max_depth):
        nxt = set()
        for edge in core.edges:
            if edge.target in frontier:
                trace.append(edge.model_dump())
                nxt.add(edge.source)
        frontier = nxt
        if not frontier:
            break
    return {"status": "ok", "node_id": node_id, "trace": trace}

def trace_downstream(node_id: str, max_depth: int = 3):
    core = load_context_core()
    if not core:
        return {"status": "missing_context_core", "trace": []}
    trace, frontier = [], {node_id}
    for _ in range(max_depth):
        nxt = set()
        for edge in core.edges:
            if edge.source in frontier:
                trace.append(edge.model_dump())
                nxt.add(edge.target)
        frontier = nxt
        if not frontier:
            break
    return {"status": "ok", "node_id": node_id, "trace": trace}
