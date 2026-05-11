
from __future__ import annotations

from uuid import uuid4
from .angle_library import build_angle_library
from .prompt_compiler import build_visual_prompt, build_video_prompt, compile_provider_payloads
from .schemas import MultiAngleRequest, MultiAngleScene, MultiAngleStoryboard


def _time_range(start: float, duration: float) -> str:
    end = start + duration
    return f"{start:.1f}-{end:.1f}s"


def build_single_image_multi_angle_storyboard(req: MultiAngleRequest) -> MultiAngleStoryboard:
    angles = build_angle_library(
        req.subject_type,
        include_detail_shots=req.include_detail_shots,
        include_dynamic_shots=req.include_dynamic_shots,
        include_lifestyle_shots=req.include_lifestyle_shots,
    )

    # Fit to requested duration by priority and sequence energy.
    selected = sorted(angles, key=lambda a: (a.priority, a.group))[: max(5, min(len(angles), int(req.duration_seconds / 1.5)))]
    selected = sorted(selected, key=lambda a: a.priority)

    scenes = []
    cursor = 0.0
    for idx, angle in enumerate(selected, start=1):
        if cursor >= req.duration_seconds:
            break
        duration = min(angle.duration, max(1.0, req.duration_seconds - cursor))
        angle.duration = duration

        visual_prompt = build_visual_prompt(angle, req.subject_type, req.product_name, req.brand, req.style)
        video_prompt = build_video_prompt(angle, req.subject_type, req.product_name, req.brand, req.style)
        payloads = compile_provider_payloads(angle, video_prompt, req.provider_priority, req.aspect_ratio)

        goal = "Hook / hero reveal" if idx == 1 else (
            "Show angle diversity" if angle.group in ["exterior_static", "dynamic_motion", "aerial"] else
            "Detail proof / material credibility" if angle.group == "detail" else
            "Lifestyle context / conversion trust"
        )

        scenes.append(MultiAngleScene(
            scene_id=f"angle_scene_{idx:02d}",
            time_range=_time_range(cursor, duration),
            goal=goal,
            source_angle=angle,
            visual_prompt=visual_prompt,
            video_prompt=video_prompt,
            provider_payloads=payloads,
            quality_rules=[
                "REFERENCE_IDENTITY_LOCK_REQUIRED",
                "NO_COLOR_OR_MODEL_DRIFT",
                "NO_GEOMETRY_MORPHING",
                "MOBILE_SAFE_FRAMING",
                "ANGLE_LABEL_MUST_MATCH_PROMPT",
            ],
        ))
        cursor += duration

    storyboard_id = f"multi_angle_{uuid4().hex[:10]}"

    return MultiAngleStoryboard(
        storyboard_id=storyboard_id,
        input_image=req.image_url or req.image_path,
        subject_type=req.subject_type,
        brand=req.brand,
        product_name=req.product_name,
        aspect_ratio=req.aspect_ratio,
        duration_seconds=req.duration_seconds,
        angle_library=angles,
        scenes=scenes,
        reference_sheet_plan={
            "enabled": req.generate_reference_sheet,
            "groups": [
                "exterior_static/all_angles",
                "dynamic_motion/camera_moves",
                "details/closeups",
                "lifestyle/context",
                "aerial/top_views",
            ],
            "purpose": "Create a controllable angle map before expensive provider rendering."
        },
        render_package_patch={
            "render_mode": "single_image_multi_angle",
            "source_image": req.image_url or req.image_path,
            "identity_lock": True,
            "provider_strategy": "try providers by priority per scene; fallback on failure",
            "scene_count": len(scenes),
            "handoff": [
                {
                    "scene_id": s.scene_id,
                    "time_range": s.time_range,
                    "angle": s.source_angle.label,
                    "payloads": s.provider_payloads,
                }
                for s in scenes
            ],
        },
    )
