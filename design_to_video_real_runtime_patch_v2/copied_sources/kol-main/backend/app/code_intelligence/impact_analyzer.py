
from __future__ import annotations

from .schemas import CodeKnowledgeGraph


def analyze_change_impact(graph: CodeKnowledgeGraph, changed_paths: list[str]) -> dict:
    changed_ids = {f"file:{path}" for path in changed_paths}
    impacted = set(changed_ids)
    reasons = []

    for edge in graph.edges:
        if edge.source in changed_ids:
            impacted.add(edge.target)
            reasons.append({"source": edge.source, "target": edge.target, "reason": edge.type})
        if edge.target in changed_ids:
            impacted.add(edge.source)
            reasons.append({"source": edge.target, "target": edge.source, "reason": f"reverse:{edge.type}"})

    domain_counts: dict[str, int] = {}
    layer_counts: dict[str, int] = {}
    for node in graph.nodes:
        if node.id in impacted:
            domain_counts[node.domain] = domain_counts.get(node.domain, 0) + 1
            layer_counts[node.layer] = layer_counts.get(node.layer, 0) + 1

    return {
        "changed_paths": changed_paths,
        "impacted_node_count": len(impacted),
        "impacted_nodes": sorted(impacted),
        "domain_counts": domain_counts,
        "layer_counts": layer_counts,
        "reasons": reasons[:300],
        "recommended_checks": recommend_checks(domain_counts, layer_counts),
    }


def recommend_checks(domain_counts: dict[str, int], layer_counts: dict[str, int]) -> list[str]:
    checks = []

    if "storyboard-engine" in domain_counts or "multi-angle-storyboard" in domain_counts:
        checks += ["pytest backend/tests/test_poster_video_render_execution_mode.py", "python scripts/smoke_v9_single_image_multi_angle.py"]

    if "production-render" in domain_counts or "render-orchestrator" in domain_counts:
        checks += ["pytest backend/tests/test_production_hardening.py", "python scripts/smoke_v5_production_render.py"]

    if "smart-subtitle" in domain_counts:
        checks += ["python scripts/smoke_p17_smart_subtitle.py"]

    if "multi-provider" in domain_counts:
        checks += ["pytest backend/tests/providers", "pytest backend/tests/test_provider_router_failover.py"]

    if "audio-engine" in domain_counts:
        checks += ["pytest backend/tests/test_asr_alignment.py", "pytest backend/tests/test_drama_tts.py"]

    if "production-coordinator" in domain_counts:
        checks += ["pytest backend/tests/test_graph_production_coordinator.py"]

    if "vite-render-studio" in layer_counts:
        checks += ["cd frontend && npm run build"]

    if "fastapi-api-router" in layer_counts:
        checks += ["python -m compileall backend/app/api backend/app/production_coordinator backend/app/code_intelligence"]

    return checks or ["python -m compileall backend/app", "pytest backend/tests"]
