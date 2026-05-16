from __future__ import annotations

from typing import Any, Dict


SEEDANCE_MVP_PROMPT = (
    "Luxury Korean fashion commercial, cinematic pastel lighting, "
    "female model walking toward camera, soft cloth motion, dynamic hair movement, "
    "premium beauty advertising, shallow depth of field, cinematic realism"
)


def build_seedance_mvp_prompt(scene_index: int, total_scenes: int, aspect_ratio: str = "9:16") -> Dict[str, Any]:
    """Return the compact prompt preset used for Seedance Fast MVP tests."""
    return {
        "prompt": f"{SEEDANCE_MVP_PROMPT}, scene {scene_index} of {total_scenes}, {aspect_ratio}",
        "motion": "medium",
        "camera": "dynamic",
        "aspect_ratio": aspect_ratio,
        "duration": 5,
        "model": "bytedance/seedance-2-fast",
        "preset": "seedance_mvp_v1",
    }