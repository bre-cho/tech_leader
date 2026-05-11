
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .domain_pipeline import build_pipeline_nodes_and_edges
from .repo_scanner import detect_domain, detect_layer, iter_source_files
from .schemas import CodeGraphEdge, CodeGraphNode, CodeKnowledgeGraph
from .static_analyzer import analyze_python, analyze_typescript, summarize_file


def build_code_knowledge_graph(repo_root: str) -> CodeKnowledgeGraph:
    repo = Path(repo_root)
    nodes: dict[str, CodeGraphNode] = {}
    edges: list[CodeGraphEdge] = []
    domains: dict[str, list[str]] = defaultdict(list)

    for path in iter_source_files(repo_root):
        rel = path.relative_to(repo)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""

        file_id = f"file:{rel.as_posix()}"
        layer = detect_layer(rel)
        domain = detect_domain(rel, text)
        domains[domain].append(file_id)

        nodes[file_id] = CodeGraphNode(
            id=file_id,
            type="file",
            name=rel.name,
            path=rel.as_posix(),
            layer=layer,
            domain=domain,
            summary=summarize_file(rel, text),
            metadata={"size_bytes": path.stat().st_size},
        )

        if rel.suffix == ".py":
            extracted_nodes, extracted_edges = analyze_python(rel, text)
        elif rel.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            extracted_nodes, extracted_edges = analyze_typescript(rel, text)
        else:
            extracted_nodes, extracted_edges = [], []

        for item in extracted_nodes:
            node_id = item["id"]
            nodes[node_id] = CodeGraphNode(
                id=node_id,
                type=item["type"],
                name=item["name"],
                path=item.get("path"),
                layer=layer,
                domain=domain,
                summary=summarize_file(rel, text),
            )

        edges.extend(CodeGraphEdge(**item) for item in extracted_edges)

    pipeline_nodes, pipeline_edges = build_pipeline_nodes_and_edges()
    for node in pipeline_nodes:
        nodes[node.id] = node
        domains[node.domain].append(node.id)
    edges.extend(pipeline_edges)

    tours = [
        {
            "tour_id": "closed-loop-video-production",
            "title": "Closed-loop production of one complete video",
            "steps": [n.id for n in pipeline_nodes],
        },
        {
            "tour_id": "new-dev-onboarding",
            "title": "New developer onboarding for kol-main(11)",
            "steps": [
                "backend/main.py",
                "backend/app/api/_registry.py",
                "backend/app/api/poster_video_render_routes.py",
                "backend/app/storyboard_to_render_bridge.py",
                "backend/app/api/production_render_routes.py",
                "frontend/src/App.tsx",
            ],
        },
        {
            "tour_id": "ai-agent-safe-patch-flow",
            "title": "AI Agent safe patch workflow",
            "steps": [
                "Build graph",
                "Query target domain",
                "Run impact analysis",
                "Patch only affected layer",
                "Run recommended checks",
                "Rebuild graph and commit updated graph",
            ],
        },
    ]

    return CodeKnowledgeGraph(
        graph_id=f"code_graph_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        repo_root=repo_root,
        generated_at=datetime.now(timezone.utc).isoformat(),
        nodes=list(nodes.values()),
        edges=edges,
        domains=dict(domains),
        tours=tours,
    )
