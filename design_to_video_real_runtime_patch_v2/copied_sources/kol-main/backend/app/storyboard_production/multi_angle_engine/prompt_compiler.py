
from __future__ import annotations

from typing import Any, Dict, List
from .schemas import AngleSpec, ProviderName


def continuity_block(subject_type: str, product_name: str | None, brand: str | None) -> str:
    subject = product_name or subject_type
    brand_line = f" Brand identity: {brand}." if brand else ""
    return (
        f"Use the uploaded source image as the strict identity/reference source for the {subject}. "
        f"Preserve exact color palette, shape language, proportions, material finish, logo placement, and key visual identity.{brand_line} "
        "When generating unseen angles, infer geometry consistently from the reference image. "
        "No redesign, no random color change, no extra logos, no wrong model details."
    )


def build_visual_prompt(angle: AngleSpec, subject_type: str, product_name: str | None, brand: str | None, style: str) -> str:
    return (
        f"{continuity_block(subject_type, product_name, brand)} "
        f"Create a high-fidelity keyframe for angle: {angle.label}. "
        f"Shot size: {angle.shot_size}. Camera angle: {angle.camera_angle}. Lens: {angle.lens}. "
        f"Goal: {angle.prompt_intent}. Style: {style}. "
        "Premium commercial lighting, sharp details, realistic perspective, clean composition, mobile-safe framing."
    )


def build_video_prompt(angle: AngleSpec, subject_type: str, product_name: str | None, brand: str | None, style: str) -> str:
    return (
        "Animate the static keyframe into a realistic AI video shot. "
        f"{continuity_block(subject_type, product_name, brand)} "
        f"Camera movement: {angle.camera_motion}. Angle: {angle.label}. "
        "Use controlled micro-motions, realistic parallax, natural lighting changes, subtle reflections and depth. "
        "Avoid morphing, melting geometry, incorrect identity, distorted text, unstable logos, excessive fast motion. "
        f"Commercial cinematic style: {style}."
    )


def compile_provider_payloads(angle: AngleSpec, video_prompt: str, providers: List[ProviderName], aspect_ratio: str) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for provider in providers:
        if provider == "seedance2":
            payloads.append({
                "provider": "seedance2",
                "mode": "image_to_video",
                "duration": angle.duration,
                "aspect_ratio": aspect_ratio,
                "prompt": video_prompt,
                "camera_motion": angle.camera_motion,
                "negative_prompt": "morphing, geometry drift, wrong angle, color change, watermark, text errors"
            })
        elif provider == "kling":
            payloads.append({
                "provider": "kling",
                "mode": "image_to_video",
                "duration": angle.duration,
                "aspect_ratio": aspect_ratio,
                "prompt": video_prompt,
                "cfg": 0.65,
                "motion_strength": "medium"
            })
        elif provider == "runway":
            payloads.append({
                "provider": "runway",
                "mode": "image_to_video",
                "duration": angle.duration,
                "aspect_ratio": aspect_ratio,
                "promptText": video_prompt,
                "seed_strategy": "lock_reference_identity"
            })
        elif provider == "veo":
            payloads.append({
                "provider": "veo",
                "mode": "image_to_video",
                "duration": angle.duration,
                "aspect_ratio": aspect_ratio,
                "veo_json_payload": {
                    "prompt": video_prompt,
                    "style": ["cinematic commercial", "realistic", "premium", "smooth camera"],
                    "camera_movement": [angle.camera_motion, angle.shot_size],
                    "negative_prompt": "morphing, distorted features, wrong model, unstable text, watermark"
                }
            })
        elif provider == "html_motion":
            payloads.append({
                "provider": "html_motion",
                "mode": "template_scene",
                "duration": angle.duration,
                "aspect_ratio": aspect_ratio,
                "template": angle.group,
                "motion": angle.camera_motion
            })
    return payloads
