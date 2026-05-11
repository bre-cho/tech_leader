
from datetime import datetime, timezone
from uuid import uuid4
from .graph_store import load_context_core
from .schemas import ContextPipelinePlan, ContextRun, PipelineContextRequest, PipelineDecision, ProvenanceRef

# In-memory run registry (dev/test fallback; replace with DB-backed store for production).
_run_registry: dict[str, ContextRun] = {}


def get_context_run(run_id: str) -> ContextRun | None:
    """Retrieve a persisted ContextRun from the in-memory registry by run_id.

    Note: This is a dev/test fallback. In production, replace with a DB-backed
    lookup so runs are durable across process restarts and queryable by operators.
    Returns None if no run with the given ID is found.
    """
    return _run_registry.get(run_id)


def build_context_pipeline_plan(req: PipelineContextRequest) -> ContextPipelinePlan:
    run_id = f"run_{uuid4().hex[:12]}"
    core = load_context_core()
    if not core:
        plan = ContextPipelinePlan(
            plan_id=f"context_plan_{uuid4().hex[:10]}",
            context_core_id="missing",
            status="blocked",
            decisions=[],
            missing_inputs=["context_core"],
            warnings=["Run POST /api/trustgraph-runtime/build-core first."],
        )
        _persist_run(run_id, plan, req)
        return plan

    missing_inputs, warnings, decisions = [], [], []

    node_by_id = {node.id: node for node in core.nodes}
    # Always require the input contract node to have a real value.
    if not req.poster_image_url and not req.poster_image_path and not req.campaign_brief:
        missing_inputs.append("poster_image_or_campaign_brief")

    edge_map: dict[str, list] = {}
    for edge in core.edges:
        edge_map.setdefault(edge.source, []).append(edge)

    ordered_modules = [
        "module:poster_analyzer","module:storyboard_engine","module:multi_angle",
        "module:drama_engine","module:cinematic_language_engine","module:higgsfield_seedance2","module:provider_router",
        "module:html_render","module:audio_engine","module:avatar_engine","module:smart_subtitle",
        "module:production_render","module:artifact_storage","module:analytics_feedback",
    ]

    disabled = set()
    if not req.poster_image_url and not req.poster_image_path:
        disabled.add("module:multi_angle")
        warnings.append("No source image provided; multi-angle step will be skipped.")

    for idx, module_id in enumerate(ordered_modules, start=1):
        if module_id in disabled:
            continue
        node = node_by_id.get(module_id)
        if not node:
            continue
        outgoing = edge_map.get(module_id, [])
        expected_outputs = [e.target for e in outgoing if e.type in {"produces","next_step"}]
        fallbacks = [e.target for e in outgoing if e.type == "fallback_to"]
        blocking = [
            n.summary for n in core.nodes
            if n.type == "policy" and (
                ("NO_AUDIO" in n.summary and module_id == "module:audio_engine") or
                ("NO_STORYBOARD" in n.summary and module_id == "module:storyboard_engine") or
                ("NO_FINAL" in n.summary and module_id in {"module:production_render","module:artifact_storage"})
            )
        ]
        decisions.append(PipelineDecision(
            decision_id=f"decision_{idx:02d}_{uuid4().hex[:6]}",
            step_id=module_id,
            selected_module=module_id,
            reason=f"Selected {node.name} because context core maps it to domain {node.domain}.",
            required_inputs=[e.source for e in core.edges if e.target == module_id and e.type in {"consumes","requires"}],
            expected_outputs=expected_outputs,
            fallback_options=fallbacks,
            blocking_policies=blocking,
            evidence=node.provenance or [ProvenanceRef(source_type="context_core", source_id=core.core_id, confidence=0.9)],
        ))

    plan = ContextPipelinePlan(
        plan_id=f"context_plan_{uuid4().hex[:10]}",
        context_core_id=core.core_id,
        status="blocked" if missing_inputs else "ready",
        decisions=decisions,
        missing_inputs=missing_inputs,
        execution_order=[d.step_id for d in decisions],
        final_contract_requirements=[
            "final_video_artifact.path_or_url",
            "final_video_artifact.mime_type == video/mp4",
            "final_video_artifact.size_bytes > 0",
            "final_video_artifact.checksum",
            "final_video_artifact.duration_seconds",
            "final_video_artifact.aspect_ratio",
            "source_scene_artifacts[]",
            "audio_artifact",
            "subtitle_artifact",
            "provenance[]",
        ],
        warnings=warnings,
    )
    _persist_run(run_id, plan, req)
    return plan


def _persist_run(run_id: str, plan: ContextPipelinePlan, req: PipelineContextRequest) -> None:
    """Persist a ContextRun record for audit and replay."""
    _run_registry[run_id] = ContextRun(
        run_id=run_id,
        plan_id=plan.plan_id,
        context_core_id=plan.context_core_id,
        status="blocked" if plan.missing_inputs else "pending",
        decisions=plan.decisions,
        missing_inputs=plan.missing_inputs,
        warnings=plan.warnings,
        started_at=datetime.now(timezone.utc).isoformat(),
    )
