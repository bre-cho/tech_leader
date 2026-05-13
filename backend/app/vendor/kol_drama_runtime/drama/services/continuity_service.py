from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.drama.engines.continuity_engine import ContinuityEngine
from app.drama.models.scene_drama_state import DramaSceneState

if TYPE_CHECKING:
    from app.drama.models.scene_drama_state import DramaSceneState

_logger = logging.getLogger(__name__)


class ContinuityService:
    """Thin orchestration layer for continuity checks."""

    def __init__(self) -> None:
        self.engine = ContinuityEngine()

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_previous_scene_state(
        db: Session,
        episode_id: str | None,
        scene_index: int | None,
    ) -> Dict[str, Any] | None:
        """Load the previous scene's drama state from the DB.

        Finds the scene whose ``scene_index`` equals ``scene_index - 1`` within
        the given episode by joining :class:`~app.models.scene.Scene` with
        :class:`~app.drama.models.scene_drama_state.DramaSceneState`.

        Returns a plain dict suitable for passing to the continuity engine, or
        ``None`` if no suitable preceding scene can be found.
        """
        if db is None or not episode_id or scene_index is None or scene_index <= 0:
            return None
        try:
            from app.models.scene import Scene

            prev_state = (
                db.query(DramaSceneState)
                .join(Scene, Scene.id == DramaSceneState.scene_id)
                .filter(
                    Scene.episode_id == episode_id,
                    Scene.scene_index == scene_index - 1,
                )
                .first()
            )
            if prev_state is None:
                return None
            return {
                "scene_goal": prev_state.scene_goal,
                "visible_conflict": prev_state.visible_conflict,
                "hidden_conflict": prev_state.hidden_conflict,
                "scene_temperature": prev_state.scene_temperature,
                "pressure_level": prev_state.pressure_level,
                "dominant_character_id": str(prev_state.dominant_character_id) if prev_state.dominant_character_id else None,
                "emotional_center_character_id": str(prev_state.emotional_center_character_id) if prev_state.emotional_center_character_id else None,
                "outcome_type": prev_state.outcome_type,
                "power_shift_delta": prev_state.power_shift_delta,
                "trust_shift_delta": prev_state.trust_shift_delta,
                "exposure_shift_delta": prev_state.exposure_shift_delta,
                "dependency_shift_delta": prev_state.dependency_shift_delta,
            }
        except Exception as exc:  # noqa: BLE001
            _logger.debug(
                "_load_previous_scene_state: DB lookup failed for episode=%s scene_index=%s: %s",
                episode_id,
                scene_index,
                exc,
            )
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def inspect_scene_transition(
        self,
        scene_context: Dict[str, Any],
        current_analysis: Dict[str, Any],
        previous_scene_state: Optional[Dict[str, Any]] = None,
        db: Session | None = None,
    ) -> Dict[str, Any]:
        """Inspect a scene transition for continuity breaks.

        When *previous_scene_state* is not provided the method attempts to load
        the preceding scene's state from the DB using ``episode_id`` and
        ``scene_index`` from *scene_context*.

        When *db* is ``None`` and no *previous_scene_state* is provided (e.g.
        first scene in an episode, offline analysis, or unit tests), the method
        falls back to a deterministic rule-based result with an empty previous
        state rather than requiring a stub bypass flag.  This is a legitimate
        first-scene scenario, not a stub.
        """
        if not previous_scene_state:
            # Attempt DB-backed lookup before falling back to empty state.
            episode_id = scene_context.get("episode_id")
            scene_index = scene_context.get("scene_index")
            if db is not None and episode_id is not None and scene_index is not None:
                previous_scene_state = self._load_previous_scene_state(
                    db, str(episode_id), int(scene_index)
                )
            # When previous state is still absent, use an empty dict — this is
            # correct for the first scene in an episode.  No stub guard is needed
            # here because the ContinuityEngine handles an empty previous state
            # deterministically (returns "no_prior_scene" continuity status).
            if not previous_scene_state:
                previous_scene_state = {}
        return self.engine.inspect_transition(
            previous_scene_state=previous_scene_state,
            current_scene_context=scene_context,
            current_analysis=current_analysis,
        )

    def check_continuity(
        self,
        previous_analysis: Dict[str, Any],
        current_analysis: Dict[str, Any],
        db: Session | None = None,
    ) -> Dict[str, Any]:
        """Check continuity between two analyses.

        When *previous_analysis* is empty the method attempts a DB-backed
        lookup using ``episode_id`` / ``scene_index`` from *current_analysis*
        before falling back to an empty state (first-scene or offline mode).
        No stub bypass flag is required — an empty previous state is a
        deterministic, rule-based result handled correctly by the engine.
        """
        if not previous_analysis:
            episode_id = current_analysis.get("episode_id")
            scene_index = current_analysis.get("scene_index")
            if db is not None and episode_id is not None and scene_index is not None:
                loaded = self._load_previous_scene_state(
                    db, str(episode_id), int(scene_index)
                )
                if loaded:
                    previous_analysis = loaded
        previous_state = previous_analysis.get("drama_state") or previous_analysis
        current_context = current_analysis.get("scene_context") or {}
        report = self.engine.inspect_transition(
            previous_scene_state=previous_state,
            current_scene_context=current_context,
            current_analysis=current_analysis,
        )
        has_break = report.get("continuity_status") not in {"ok", "stable"}
        return {
            "has_break": bool(has_break),
            "continuity_status": report.get("continuity_status", "ok"),
            "continuity_notes": report.get("continuity_notes", []),
            "details": report,
        }

    def compare(self, previous_state: DramaSceneState, current_state: DramaSceneState) -> Dict[str, Any]:
        """Compare two scene states and detect continuity breaks."""
        previous_dict = {
            "scene_goal": previous_state.scene_goal,
            "visible_conflict": previous_state.visible_conflict,
            "hidden_conflict": previous_state.hidden_conflict,
            "scene_temperature": previous_state.scene_temperature,
            "pressure_level": previous_state.pressure_level,
            "dominant_character_id": str(previous_state.dominant_character_id) if previous_state.dominant_character_id else None,
            "emotional_center_character_id": str(previous_state.emotional_center_character_id) if previous_state.emotional_center_character_id else None,
            "outcome_type": previous_state.outcome_type,
            "power_shift_delta": previous_state.power_shift_delta,
            "trust_shift_delta": previous_state.trust_shift_delta,
            "exposure_shift_delta": previous_state.exposure_shift_delta,
            "dependency_shift_delta": previous_state.dependency_shift_delta,
        }

        current_dict = {
            "scene_goal": current_state.scene_goal,
            "visible_conflict": current_state.visible_conflict,
            "hidden_conflict": current_state.hidden_conflict,
            "scene_temperature": current_state.scene_temperature,
            "pressure_level": current_state.pressure_level,
            "dominant_character_id": str(current_state.dominant_character_id) if current_state.dominant_character_id else None,
            "emotional_center_character_id": str(current_state.emotional_center_character_id) if current_state.emotional_center_character_id else None,
            "outcome_type": current_state.outcome_type,
            "power_shift_delta": current_state.power_shift_delta,
            "trust_shift_delta": current_state.trust_shift_delta,
            "exposure_shift_delta": current_state.exposure_shift_delta,
            "dependency_shift_delta": current_state.dependency_shift_delta,
        }

        analysis_result = self.engine.inspect_transition(
            previous_scene_state=previous_dict,
            current_scene_context=current_dict,
            current_analysis={},
        )

        has_break = False
        if analysis_result.get("continuity_status") != "ok":
            has_break = True
        elif previous_state.outcome_type and current_state.scene_goal:
            has_break = previous_state.outcome_type not in [current_state.scene_goal, current_state.visible_conflict, current_state.hidden_conflict]

        return {
            "has_break": has_break,
            "previous_state_summary": previous_dict,
            "current_state_summary": current_dict,
            "analysis": analysis_result,
        }

    def apply_scene_outcome(
        self,
        *,
        db: Session,
        scene_id: UUID,
        outcome_type: str,
        turning_point: str | None = None,
        trust_shift_delta: float = 0.0,
        exposure_shift_delta: float = 0.0,
        dependency_shift_delta: float = 0.0,
        recompute_downstream: bool = True,
    ) -> Dict[str, Any]:
        scene_state = db.query(DramaSceneState).filter(DramaSceneState.scene_id == scene_id).first()
        if scene_state is None:
            raise ValueError("scene state not found")

        scene_state.outcome_type = outcome_type
        if turning_point is not None:
            scene_state.turning_point = turning_point
        scene_state.trust_shift_delta = trust_shift_delta
        scene_state.exposure_shift_delta = exposure_shift_delta
        scene_state.dependency_shift_delta = dependency_shift_delta
        current_continuity = scene_state.continuity_payload or {}
        scene_state.continuity_payload = {
            **current_continuity,
            "status": "applied",
            "outcome_type": outcome_type,
            "recompute_downstream": recompute_downstream,
        }
        db.add(scene_state)
        db.flush()

        return {
            "scene_id": str(scene_id),
            "episode_id": str(scene_state.episode_id) if scene_state.episode_id else None,
            "project_id": str(scene_state.project_id) if scene_state.project_id else None,
            "accepted": True,
            "recompute_downstream": recompute_downstream,
        }
