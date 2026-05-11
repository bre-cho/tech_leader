
from __future__ import annotations

from typing import Dict, List
from .schemas import MultiAngleStoryboard


def validate_multi_angle_storyboard(storyboard: MultiAngleStoryboard) -> Dict:
    errors: List[str] = []
    warnings: List[str] = []

    if not storyboard.input_image:
        errors.append("NO_SOURCE_IMAGE")

    if len(storyboard.scenes) < 5:
        errors.append("NOT_ENOUGH_ANGLE_SCENES")

    seen = set()
    for scene in storyboard.scenes:
        aid = scene.source_angle.angle_id
        if aid in seen:
            warnings.append(f"DUPLICATE_ANGLE:{aid}")
        seen.add(aid)

        if not scene.provider_payloads:
            errors.append(f"NO_PROVIDER_PAYLOAD:{scene.scene_id}")
        if "Preserve exact color palette" not in scene.video_prompt:
            errors.append(f"NO_IDENTITY_LOCK_PROMPT:{scene.scene_id}")
        if scene.source_angle.duration <= 0:
            errors.append(f"INVALID_DURATION:{scene.scene_id}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "scene_count": len(storyboard.scenes),
        "angle_count": len(storyboard.angle_library),
    }
