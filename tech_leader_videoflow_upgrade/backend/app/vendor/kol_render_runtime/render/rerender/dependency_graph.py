from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RerenderImpactPlan:
    changed_scene_index: int
    affected_scene_indexes: list[int]
    requires_audio_rebuild: bool
    requires_subtitle_rebuild: bool
    requires_smart_reassembly: bool
    reason: str


def build_rerender_dependency_graph(
    *,
    timeline: dict[str, Any] | None,
    changed_scene_index: int,
    change_type: str,
) -> RerenderImpactPlan:
    """Compute the minimum safe rerender/reassembly impact set.

    Rules:
    - visual-only change affects only the selected scene.
    - audio/subtitle/duration changes require selected scene and all following
      scenes because subtitle offsets and final timeline timestamps shift.
    - unknown/both changes are conservative and reassemble selected scene onward.
    """
    scenes = []
    if isinstance(timeline, dict):
        scenes = timeline.get("scenes") or []
    indexes = [int(s.get("scene_index", i)) for i, s in enumerate(scenes)] or [changed_scene_index]
    if changed_scene_index not in indexes:
        indexes.append(changed_scene_index)
        indexes.sort()

    normalized = (change_type or "both").lower()
    if normalized in {"video", "visual", "camera", "style"}:
        affected = [changed_scene_index]
        return RerenderImpactPlan(changed_scene_index, affected, False, False, True, "visual_only")

    affected = [i for i in indexes if i >= changed_scene_index]
    return RerenderImpactPlan(
        changed_scene_index=changed_scene_index,
        affected_scene_indexes=affected,
        requires_audio_rebuild=normalized in {"audio", "voice", "voiceover", "both", "duration", "subtitle"},
        requires_subtitle_rebuild=True,
        requires_smart_reassembly=True,
        reason="timeline_shift_risk",
    )
