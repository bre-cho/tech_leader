
from __future__ import annotations

from app.code_intelligence.schemas import CodeKnowledgeGraph


def resolve_modules_for_domain(graph: CodeKnowledgeGraph | None, domain: str, limit: int = 12) -> tuple[list[dict], list[dict]]:
    if graph is None:
        return [], []

    module_candidates = []
    api_candidates = []

    for node in graph.nodes:
        if node.domain != domain:
            continue

        if node.type in {"file", "class", "function", "worker_task", "provider_adapter", "pipeline_step"}:
            module_candidates.append(
                {
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "path": node.path,
                    "layer": node.layer,
                    "summary": node.summary,
                }
            )

        if node.type == "api_route":
            api_candidates.append(
                {
                    "id": node.id,
                    "name": node.name,
                    "path": node.path,
                    "summary": node.summary,
                }
            )

        if len(module_candidates) >= limit and len(api_candidates) >= limit:
            break

    return module_candidates[:limit], api_candidates[:limit]
