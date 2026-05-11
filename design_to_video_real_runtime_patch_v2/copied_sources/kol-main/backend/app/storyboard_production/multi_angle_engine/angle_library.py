
from __future__ import annotations

from typing import List
from .schemas import AngleSpec


def build_angle_library(subject_type: str, include_detail_shots: bool = True, include_dynamic_shots: bool = True, include_lifestyle_shots: bool = True) -> List[AngleSpec]:
    """Return production-ready angle grammar from a single input image.

    The engine does not assume the source image contains every angle.
    It creates controlled synthetic angle targets while preserving identity/style/color/material.
    """

    base: List[AngleSpec] = [
        AngleSpec(angle_id="front", label="Front View", group="exterior_static", shot_size="medium wide", camera_angle="front eye-level", camera_motion="slow push-in", lens="50mm", duration=2.5, priority=1, prompt_intent="reconstruct subject from front angle"),
        AngleSpec(angle_id="front_34_left", label="Front 3/4 Left", group="exterior_static", shot_size="wide hero", camera_angle="front three-quarter left", camera_motion="slow dolly-in", lens="35mm anamorphic", duration=2.5, priority=1, prompt_intent="hero reveal with dimensional depth"),
        AngleSpec(angle_id="front_34_right", label="Front 3/4 Right", group="exterior_static", shot_size="wide hero", camera_angle="front three-quarter right", camera_motion="slow orbit right", lens="35mm anamorphic", duration=2.5, priority=2, prompt_intent="alternate hero reveal"),
        AngleSpec(angle_id="side_left", label="Side View Left", group="exterior_static", shot_size="wide profile", camera_angle="perfect left side profile", camera_motion="slow lateral slide", lens="70mm", duration=2.5, priority=1, prompt_intent="clean silhouette/profile angle"),
        AngleSpec(angle_id="side_right", label="Side View Right", group="exterior_static", shot_size="wide profile", camera_angle="perfect right side profile", camera_motion="slow lateral slide", lens="70mm", duration=2.5, priority=2, prompt_intent="right silhouette/profile angle"),
        AngleSpec(angle_id="rear", label="Rear View", group="exterior_static", shot_size="medium wide", camera_angle="rear eye-level", camera_motion="slow pull-back", lens="50mm", duration=2.0, priority=2, prompt_intent="rear identity and design language"),
        AngleSpec(angle_id="rear_34_left", label="Rear 3/4 Left", group="exterior_static", shot_size="wide hero", camera_angle="rear three-quarter left", camera_motion="slow orbit left", lens="35mm anamorphic", duration=2.5, priority=2, prompt_intent="rear cinematic reveal"),
        AngleSpec(angle_id="top", label="Top View", group="exterior_static", shot_size="overhead", camera_angle="top-down overhead", camera_motion="vertical crane down", lens="35mm", duration=2.0, priority=3, prompt_intent="top layout and shape reconstruction"),
        AngleSpec(angle_id="low_angle", label="Low Angle Hero", group="cinematic", shot_size="low wide", camera_angle="low angle hero", camera_motion="slow rise up", lens="28mm", duration=2.5, priority=1, prompt_intent="powerful hero perspective"),
        AngleSpec(angle_id="macro_texture", label="Macro Texture", group="detail", shot_size="extreme close-up", camera_angle="macro detail", camera_motion="rack focus", lens="100mm macro", duration=1.8, priority=2, prompt_intent="material and texture proof"),
    ]

    details = [
        AngleSpec(angle_id="detail_logo", label="Logo/Badge Close-up", group="detail", shot_size="extreme close-up", camera_angle="macro frontal", camera_motion="micro push-in", lens="100mm macro", duration=1.5, priority=2, prompt_intent="brand badge/logo detail"),
        AngleSpec(angle_id="detail_wheel_or_hand", label="Wheel/Hand/Product Detail", group="detail", shot_size="close-up", camera_angle="detail three-quarter", camera_motion="slow slider", lens="85mm", duration=1.5, priority=2, prompt_intent="key component close-up"),
        AngleSpec(angle_id="detail_interior_or_texture", label="Interior/Fabric/Texture Detail", group="detail", shot_size="macro", camera_angle="top oblique macro", camera_motion="rack focus", lens="100mm macro", duration=1.5, priority=3, prompt_intent="interior/material texture"),
    ]

    dynamic = [
        AngleSpec(angle_id="dolly_in", label="Dolly In", group="dynamic_motion", shot_size="wide to medium", camera_angle="front hero", camera_motion="cinematic dolly-in", lens="35mm", duration=2.5, priority=1, prompt_intent="main opening motion"),
        AngleSpec(angle_id="orbit_180", label="180 Orbit", group="dynamic_motion", shot_size="wide hero", camera_angle="3/4 orbit", camera_motion="smooth 180 degree orbit", lens="35mm anamorphic", duration=3.0, priority=1, prompt_intent="show multiple angles in one shot"),
        AngleSpec(angle_id="whip_transition", label="Whip Transition", group="dynamic_motion", shot_size="medium", camera_angle="transition blur", camera_motion="fast whip pan transition", lens="35mm", duration=1.0, priority=3, prompt_intent="transition energy"),
        AngleSpec(angle_id="drone_top_follow", label="Drone / Top Follow", group="aerial", shot_size="aerial wide", camera_angle="high overhead", camera_motion="drone follow / crane drift", lens="24mm", duration=2.5, priority=3, prompt_intent="premium overhead motion"),
    ]

    lifestyle = [
        AngleSpec(angle_id="environment_hero", label="Lifestyle Hero Context", group="lifestyle", shot_size="wide contextual", camera_angle="front 3/4 environmental", camera_motion="slow push-in", lens="35mm", duration=2.5, priority=2, prompt_intent="place subject in premium environment"),
        AngleSpec(angle_id="user_interaction", label="Human/Product Interaction", group="lifestyle", shot_size="medium", camera_angle="eye-level lifestyle", camera_motion="slow handheld natural motion", lens="50mm", duration=2.0, priority=3, prompt_intent="natural human interaction or usage"),
    ]

    if include_detail_shots:
        base += details
    if include_dynamic_shots:
        base += dynamic
    if include_lifestyle_shots:
        base += lifestyle

    return base
