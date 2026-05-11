
from __future__ import annotations

from uuid import uuid4

from app.code_intelligence.service import load_graph
from .module_resolver import resolve_modules_for_domain
from .pipeline_registry import base_closed_loop_steps
from .schemas import ProductionInput, ProductionPlan


def build_production_plan(req: ProductionInput) -> ProductionPlan:
    graph = load_graph()
    steps = base_closed_loop_steps()

    toggles = {
        "multi_angle": req.enable_multi_angle,
        "higgsfield_seedance2": req.enable_higgsfield_seedance2,
        "provider_render": req.enable_provider_render,
        "html_render_fallback": req.enable_html_render_fallback,
        "audio": req.enable_audio,
        "avatar": req.enable_avatar,
        "drama": req.enable_drama,
        "subtitle": req.enable_smart_subtitle,
        "assembly": req.enable_final_assembly,
        "analytics_feedback": req.enable_analytics_feedback,
    }

    missing_required_domains: list[str] = []
    warnings: list[str] = []

    for step in steps:
        if step.step_id in toggles:
            step.enabled = bool(toggles[step.step_id])
            if not step.enabled:
                step.status = "skipped"
                step.notes.append("Disabled by ProductionInput toggle.")
                continue

        modules, apis = resolve_modules_for_domain(graph, step.domain)
        step.module_candidates = modules
        step.api_candidates = apis

        if step.required and not modules and graph is not None:
            missing_required_domains.append(step.domain)
            step.status = "blocked"
            step.notes.append("Required domain has no mapped module in code graph.")
        elif step.enabled:
            step.status = "ready"

    if graph is None:
        warnings.append("Code graph is missing. Run POST /api/code-intelligence/build first for best coordination.")
    if not req.poster_image_url and not req.poster_image_path and not req.campaign_brief:
        missing_required_domains.append("input")
        warnings.append("No poster image or campaign brief provided.")

    execution_order = [
        step.step_id
        for step in sorted(steps, key=lambda item: item.order)
        if step.enabled and step.status != "skipped"
    ]

    plan_id = f"production_plan_{uuid4().hex[:10]}"

    return ProductionPlan(
        plan_id=plan_id,
        graph_id=graph.graph_id if graph else None,
        input_summary={
            "has_image": bool(req.poster_image_url or req.poster_image_path),
            "brief_keys": sorted(req.campaign_brief.keys()),
            "duration_seconds": req.duration_seconds,
            "aspect_ratio": req.aspect_ratio,
            "platform": req.platform,
            "provider_priority": req.provider_priority,
        },
        steps=steps,
        execution_order=execution_order,
        missing_required_domains=sorted(set(missing_required_domains)),
        warnings=warnings,
        render_package_contract={
            "contract_type": "ClosedLoopVideoProductionPlan",
            "plan_id": plan_id,
            "must_produce": [
                "storyboard",
                "provider_payloads OR html_scene_artifacts",
                "scene_video_artifacts OR html_scene_artifacts",
                "mixed_audio_artifact",
                "ass_subtitle",
                "final_video_artifact",
                "final_video_contract",
            ],
            "hard_rule": "RenderPackage is only a plan. ProductionCoordinator must drive modules until FinalVideoContract exists.",
        },
    )
