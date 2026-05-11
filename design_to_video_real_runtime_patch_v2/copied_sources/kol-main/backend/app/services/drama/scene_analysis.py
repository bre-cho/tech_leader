"""scene_analysis — integration point for the drama/engines pure-function layer.

Provides :func:`drama_scene_analysis` as the canonical entry point that chains
all pure engines from ``app.drama.engines`` in the correct order and returns a
consolidated scene analysis dict compatible with the render bridge payload.

Why a separate module?
-----------------------
``app.drama.engines`` contains a set of **pure-function** engines (no DB calls,
no side effects) designed for lightweight, testable scene reasoning.  They are
distinct from the richer ``app.services.drama`` service layer, which owns the
full compilation pipeline including DB persistence and avatar acting.

This module bridges the two: callers that only need scene analysis (e.g. a
lightweight drama scoring endpoint, a test harness, or a future async pipeline)
can call :func:`drama_scene_analysis` without importing the full
:class:`~app.services.drama.drama_compiler_service.DramaCompilerService` stack.

Calling order
--------------
1.  **TensionEngine** — scene temperature, pressure, and exposure risk
2.  **CharacterIntentEngine** — per-character outer-goal / hidden-need framing
3.  **PowerShiftEngine** — power-dimension deltas from scene context
4.  **SubtextEngine** — psychological action per character pair
5.  **MemoryRecallEngine** — relevant prior memories for each character
6.  **ArcEngine** — arc stage advancement per character
7.  **BlockingEngine** — spatial blocking plan
8.  **CameraDramaEngine** — camera move and shot grammar
9.  **ContinuityEngine** — scene law validation

All engines are stateless; the caller supplies all state as arguments.

Usage
-----
::

    from app.services.drama.scene_analysis import drama_scene_analysis

    result = drama_scene_analysis(
        scene_context=scene_context,
        character_profiles=[profile_a, profile_b],
        relationship_edges=[rel_a_to_b, rel_b_to_a],
        character_arc_states={
            "char_001": {"arc_stage": "mask_stable", ...},
        },
        character_memories={
            "char_001": [memory1, memory2],
        },
        scene_history=[prev_scene_drama, ...],
        previous_scene_state=prev_state_dict,
    )
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

_logger = logging.getLogger(__name__)


def drama_scene_analysis(
    *,
    scene_context: Dict[str, Any],
    character_profiles: List[Any],
    relationship_edges: List[Any],
    character_arc_states: Optional[Dict[str, Dict[str, Any]]] = None,
    character_memories: Optional[Dict[str, List[Any]]] = None,
    scene_history: Optional[List[Dict[str, Any]]] = None,
    previous_scene_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run the full drama/engines pure-function pipeline for a scene.

    Parameters
    ----------
    scene_context:
        Scene-level dict including ``scene_id``, ``trigger_event``,
        ``exposure_risk``, ``participants``, ``dominant_character_id``, etc.
    character_profiles:
        List of character profile objects (attrs: ``id``, ``outer_goal``,
        ``hidden_need``, ``archetype``, ``mask_strategy``, …).
    relationship_edges:
        List of relationship edge objects (attrs: ``source_character_id``,
        ``target_character_id``, ``trust_level``, ``resentment_level``,
        ``dominance_source_over_target``, …).
    character_arc_states:
        Mapping ``character_id`` → arc state dict.  Missing characters start at
        ``mask_stable`` with zero pressure.
    character_memories:
        Mapping ``character_id`` → list of memory objects.
    scene_history:
        List of previous scene_drama dicts for continuity checks.
    previous_scene_state:
        Previous scene state dict for continuity engine.

    Returns
    -------
    dict
        Consolidated scene analysis with keys:
        ``tension_breakdown``, ``character_intents``, ``power_shift``,
        ``subtext_actions``, ``memory_recalls``, ``arc_results``,
        ``blocking_plan``, ``camera_plan``, ``continuity_result``.
    """
    # Lazy imports to keep this module importable even when engines are not
    # installed (e.g. in minimal test environments).
    from app.drama.engines.arc_engine import ArcEngine  # noqa: PLC0415
    from app.drama.engines.blocking_engine import BlockingEngine  # noqa: PLC0415
    from app.drama.engines.camera_drama_engine import CameraDramaEngine  # noqa: PLC0415
    from app.drama.engines.character_intent_engine import CharacterIntentEngine  # noqa: PLC0415
    from app.drama.engines.continuity_engine import ContinuityEngine  # noqa: PLC0415
    from app.drama.engines.memory_recall_engine import MemoryRecallEngine  # noqa: PLC0415
    from app.drama.engines.power_shift_engine import PowerShiftEngine  # noqa: PLC0415
    from app.drama.engines.subtext_engine import SubtextEngine  # noqa: PLC0415
    from app.drama.engines.tension_engine import TensionEngine  # noqa: PLC0415

    arc_states = character_arc_states or {}
    memories = character_memories or {}

    # -----------------------------------------------------------------------
    # 1. Character intents — computed first so TensionEngine receives actual
    #    intent objects rather than placeholder stubs.  This ensures that when
    #    TensionEngine's ML model is active, its ``intent_count`` feature
    #    reflects real derived intents and not just the character-profile list.
    # -----------------------------------------------------------------------
    intent_engine = CharacterIntentEngine()
    character_intents: list[dict[str, Any]] = []
    for profile in character_profiles:
        intent = intent_engine.derive(profile, scene_context)
        character_intents.append(intent)

    # -----------------------------------------------------------------------
    # 2. Tension — uses actual character_intents (step 1) so intent_count is
    #    based on real intent data, not character-profile count stubs.
    # -----------------------------------------------------------------------
    tension_result = TensionEngine().score(character_intents, relationship_edges, scene_context)
    # TensionEngine returns exposure_risk inside 'breakdown', not at the top level.
    # Read it from scene_context (the authoritative source) so ArcEngine receives
    # the correct value and can trigger first_exposure arc transitions when
    # exposure_risk > 0.75.
    tension_breakdown = {
        "tension_score": tension_result.get("tension_score", 0.0),
        "exposure_risk": float(scene_context.get("exposure_risk", 0.0)),
    }

    # -----------------------------------------------------------------------
    # 3. Power shift
    # -----------------------------------------------------------------------
    power_shift = PowerShiftEngine().compute(
        scene_context=scene_context,
        relationship_snapshots=relationship_edges,
    )

    # -----------------------------------------------------------------------
    # 4. Subtext actions (one per directed pair)
    # -----------------------------------------------------------------------
    subtext_engine = SubtextEngine()
    profile_map = {p.id: p for p in character_profiles}
    edge_map: dict[tuple[str, str], Any] = {
        (e.source_character_id, e.target_character_id): e
        for e in relationship_edges
    }
    subtext_actions: list[dict[str, Any]] = []
    for i, speaker in enumerate(character_profiles):
        for j, target in enumerate(character_profiles):
            if i == j:
                continue
            edge = edge_map.get((speaker.id, target.id))
            action = subtext_engine.infer_dialogue_actions(speaker, target, edge, scene_context)
            subtext_actions.append(action)

    # -----------------------------------------------------------------------
    # 5. Memory recall — top-3 relevant memories per character
    # -----------------------------------------------------------------------
    trigger = str(scene_context.get("trigger_event", "scene_turn"))
    recall_engine = MemoryRecallEngine()
    memory_recalls: dict[str, list[Any]] = {}
    for profile in character_profiles:
        char_memories = memories.get(profile.id) or []
        recalled = recall_engine.recall(memories=char_memories, trigger=trigger, limit=3)
        memory_recalls[profile.id] = recalled

    # -----------------------------------------------------------------------
    # 6. Arc advancement per character
    # -----------------------------------------------------------------------
    arc_engine = ArcEngine()
    # Build a trust snapshot from relationship edges so ContinuityEngine can
    # compare it against the previous scene state (P9: relationship_snapshot
    # was missing from scene_analysis_input, causing the relationship_shift
    # continuity rule to never trigger).
    trust_snapshot = {
        f"{e.source_character_id}->{e.target_character_id}": float(
            getattr(e, "trust_level", 0.0) or 0.0
        )
        for e in relationship_edges
    }
    scene_analysis_input = {
        "tension_breakdown": tension_breakdown,
        "power_shift": power_shift,
        "relationship_snapshot": {"trust_snapshot": trust_snapshot},
    }
    arc_results: list[dict[str, Any]] = []
    for profile in character_profiles:
        state = arc_states.get(profile.id) or {
            "character_id": profile.id,
            "arc_stage": "mask_stable",
            "pressure_index": 0.0,
            "transformation_index": 0.0,
            "truth_acceptance_level": 0.2,
        }
        arc_result = arc_engine.advance_arc(state, scene_analysis_input)
        arc_results.append(arc_result)

    # -----------------------------------------------------------------------
    # 7. Blocking plan
    # -----------------------------------------------------------------------
    blocking_plan = BlockingEngine().build_plan(
        scene_context=scene_context,
        tension_breakdown=tension_breakdown,
        power_shift=power_shift,
    )

    # -----------------------------------------------------------------------
    # 8. Camera plan
    # -----------------------------------------------------------------------
    camera_plan = CameraDramaEngine().build_camera_plan(
        scene_context=scene_context,
        tension_breakdown=tension_breakdown,
        power_shift=power_shift,
        blocking_plan=blocking_plan,
    )

    # -----------------------------------------------------------------------
    # 9. Continuity validation
    # -----------------------------------------------------------------------
    continuity_result = ContinuityEngine().inspect_transition(
        previous_scene_state=previous_scene_state or {},
        current_scene_context=scene_context,
        current_analysis=scene_analysis_input,
    )

    return {
        "tension_breakdown": tension_result,
        "character_intents": character_intents,
        "power_shift": power_shift,
        "subtext_actions": subtext_actions,
        "memory_recalls": memory_recalls,
        "arc_results": arc_results,
        "blocking_plan": blocking_plan,
        "camera_plan": camera_plan,
        "continuity_result": continuity_result,
    }
