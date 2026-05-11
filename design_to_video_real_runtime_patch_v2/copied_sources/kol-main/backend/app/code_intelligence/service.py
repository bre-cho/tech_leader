
from __future__ import annotations

from pathlib import Path

from .graph_builder import build_code_knowledge_graph
from .impact_analyzer import analyze_change_impact
from .schemas import CodeKnowledgeGraph

DEFAULT_GRAPH_PATH = Path(".code-intelligence/knowledge-graph.json")


def build_and_save_graph(repo_root: str = ".", output_path: Path = DEFAULT_GRAPH_PATH) -> CodeKnowledgeGraph:
    graph = build_code_knowledge_graph(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
    return graph


def load_graph(path: Path = DEFAULT_GRAPH_PATH) -> CodeKnowledgeGraph | None:
    if not path.exists():
        return None
    return CodeKnowledgeGraph.model_validate_json(path.read_text(encoding="utf-8"))


def query_graph(query: str, domain_filter: str | None = None, layer_filter: str | None = None, limit: int = 20) -> list[dict]:
    graph = load_graph()
    if not graph:
        return []

    q = query.lower().strip()
    results = []
    for node in graph.nodes:
        if domain_filter and node.domain != domain_filter:
            continue
        if layer_filter and node.layer != layer_filter:
            continue

        hay = f"{node.name} {node.path or ''} {node.layer} {node.domain} {node.summary}".lower()
        if q in hay or any(token in hay for token in q.split()):
            results.append(node.model_dump())
            if len(results) >= limit:
                break
    return results


def impact_for_paths(changed_paths: list[str]) -> dict:
    graph = load_graph()
    if not graph:
        return {"status": "missing_graph", "message": "Run /api/code-intelligence/build first."}
    return analyze_change_impact(graph, changed_paths)
