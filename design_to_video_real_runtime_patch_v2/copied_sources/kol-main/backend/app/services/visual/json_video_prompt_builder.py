"""json_video_prompt_builder — Cinematic Director (Giám đốc Hình ảnh & Quay phim).

Converts a reference image and its associated :class:`~app.services.strategy.shot_list_compiler.Shot`
into a **JSON Video Prompt** — a structured payload for an image-to-video (i2v)
provider (e.g. Seedance, Veo, Kling, Runway).

The video prompt captures:

* **Subject motion** — precise description of what the character does in the shot.
* **Camera movement** — cinematic camera path for the shot.
* **Environment motion** — any background or environmental movement.
* **Audio direction** — sound design intent (fed to the Audio Engine).
* **Transition intent** — how this shot connects to the next.
* **Provider options** — ready-to-use provider-specific fields.

Output schema per shot::

    {
        "shot_index": 0,
        "beat_type": "hook",
        "reference_image_role": "subject",
        "video_prompt": {
            "subject_motion": "...",
            "camera_movement": "...",
            "environment_motion": "...",
            "mood": "...",
            "duration_seconds": 3.0,
            "aspect_ratio": "9:16",
            "negative_prompt": "...",
            "transition_to_next": "jump_cut",
            "audio_direction": "...",
        },
        "provider_options": {
            "seedance": {...},
            "veo": {...},
            "runway": {...},
            "kling": {...},
        }
    }

Usage::

    director = JsonVideoPromptBuilder()
    video_prompts = director.build_all(
        shot_list,
        image_prompts,          # output of JsonImagePromptBuilder.build_all()
        context=profile.to_context(),
    )
"""
from __future__ import annotations

from typing import Any

from app.schemas.story_beat import BeatType
from app.services.strategy.shot_list_compiler import Shot, ShotList


# ---------------------------------------------------------------------------
# Subject-motion descriptions per beat
# ---------------------------------------------------------------------------

_SUBJECT_MOTION: dict[BeatType, str] = {
    BeatType.hook: (
        "Subject is completely still for 0.5s — then a slow, deliberate lean forward "
        "into the camera. Eyes remain locked. No blinking. Minimal breathing visible."
    ),
    BeatType.setup: (
        "Subject performs a single open-palm gesture outward, then settles into a "
        "relaxed upright posture. Slight natural head movement. Confident and inviting."
    ),
    BeatType.escalation: (
        "Subject speaks with increasing hand-gesture frequency. Body shifts forward. "
        "Jaw tightens slightly. Pacing of movement increases."
    ),
    BeatType.conflict: (
        "Subject crosses arms slowly and deliberately, then holds perfectly still. "
        "Eyes narrow. Minimal facial movement. Dominant, controlled presence."
    ),
    BeatType.reveal: (
        "Subject pauses completely — one full second of stillness — then delivers the "
        "line with a controlled forward nod, as if placing a fact on the table."
    ),
    BeatType.climax: (
        "Subject's entire body generates tension: slight forward lean, hands open and "
        "spread for emphasis, voice inflection peaks. Eyes wide and fully present."
    ),
    BeatType.resolution: (
        "Subject visibly relaxes: shoulders drop, posture opens, a slow exhale. "
        "Natural, easy movement. The weight lifts from the scene."
    ),
    BeatType.cta: (
        "Subject extends one arm directly toward the camera lens, index finger pointing "
        "or open palm facing the viewer. Direct, warm, energetic."
    ),
    BeatType.callback: (
        "Subject mirrors the exact posture of the hook shot — same stillness, same gaze "
        "angle — but now layered with resolution energy."
    ),
}

_ENVIRONMENT_MOTION: dict[BeatType, str] = {
    BeatType.hook: "Background is static. Focus is entirely on the subject.",
    BeatType.setup: "Subtle background ambient depth. Light bokeh drift.",
    BeatType.escalation: "Subtle camera micro-shake, environment remains stable.",
    BeatType.conflict: "Environment is completely static. Tension through stillness.",
    BeatType.reveal: "Camera pulls back gently, revealing environmental depth.",
    BeatType.climax: "Environment compresses to near-black. Only the subject exists.",
    BeatType.resolution: "Background light breathes in slowly, warm and expanding.",
    BeatType.cta: "Clean static background. No distraction from the call to action.",
    BeatType.callback: "Echo of hook — same background, slightly warmer temperature.",
}

_AUDIO_DIRECTION: dict[BeatType, str] = {
    BeatType.hook: "Music enters cold — a single low note or silence — then a sharp stinger on the hook delivery.",
    BeatType.setup: "Warm pad chord progression builds underneath the intro. Voiceover sits above mix.",
    BeatType.escalation: "Music tension build: strings or percussion ramp. Voiceover gains energy.",
    BeatType.conflict: "Music drops to minimal — bass drone only. Silence amplifies tension.",
    BeatType.reveal: "Pre-reveal silence for 0.5s, then a swell or signature hit on the reveal line.",
    BeatType.climax: "Full orchestral/epic peak. Music and VO sync perfectly at emotional high point.",
    BeatType.resolution: "Music resolves harmonically. Warm sustained chord. VO pace slows.",
    BeatType.cta: "Upbeat, energetic music tag. Clear and bright. VO direct and fast.",
    BeatType.callback: "Echo of hook motif — same musical phrase but resolved/completed.",
}

_CAMERA_MOTION_DESC: dict[str, str] = {
    "push_in": "Camera slowly pushes forward toward the subject — intimate compression",
    "pull_out": "Camera gently pulls back — reveals environment, releases tension",
    "static": "Camera locked off — stillness as a dramatic choice",
    "handheld": "Subtle handheld micro-movement — organic, documentary feel",
    "tracking": "Camera tracks smoothly alongside subject",
    "pan_left": "Camera pans left — reveals new space",
    "pan_right": "Camera pans right — reveals new space",
    "tilt_up": "Camera tilts up — heroic framing",
    "tilt_down": "Camera tilts down — vulnerability or dominance",
    "crane": "Camera rises on a crane — epic scale",
}


# ---------------------------------------------------------------------------
# Provider-specific option builders
# ---------------------------------------------------------------------------

def _seedance_options(shot: Shot, duration: float) -> dict[str, Any]:
    return {
        "enable_text_overlay_guard": True,
        "reference_mapping": [{"kind": "image", "role": "subject", "weight": 1.0}],
        "motion_strength": 0.6 if shot.camera_movement != "static" else 0.3,
    }


def _veo_options(shot: Shot, duration: float) -> dict[str, Any]:
    return {
        "cinematic_strength": "high",
        "audio_generation": True,
        "motion_intensity": "medium" if shot.camera_movement == "static" else "high",
    }


def _runway_options(shot: Shot, duration: float) -> dict[str, Any]:
    return {
        "motion_strength": 0.55,
        "style_preservation": 0.75,
    }


def _kling_options(shot: Shot, duration: float) -> dict[str, Any]:
    return {
        "cfg_scale": 0.5,
    }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class JsonVideoPromptBuilder:
    """Build JSON video prompts (image-to-video) from a :class:`ShotList`.

    Context keys consumed (from ``ProjectProfile.to_context()``):
        aspect_ratio (str): Target video aspect ratio.
        negative_prompt_defaults (str): Project-level negative prompt.
        visual_style (str): Injected into prompt for style continuity.
        music_mood (str): Carried into audio direction.
    """

    def build(
        self,
        shot: Shot,
        image_prompt: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        aspect_ratio = ctx.get("aspect_ratio", "9:16")
        negative_prompt = ctx.get(
            "negative_prompt_defaults",
            "low quality, warped anatomy, jump cuts, flicker, watermark",
        )
        visual_style = ctx.get("visual_style", "cinematic")
        music_mood = ctx.get("music_mood", "epic motivational")

        subject_motion = _SUBJECT_MOTION.get(shot.beat_type, "Subject holds position with natural breathing.")
        env_motion = _ENVIRONMENT_MOTION.get(shot.beat_type, "Static background.")
        audio_direction = _AUDIO_DIRECTION.get(shot.beat_type, "Neutral underscore.")
        camera_desc = _CAMERA_MOTION_DESC.get(shot.camera_movement, shot.camera_movement)

        video_prompt: dict[str, Any] = {
            "subject_motion": subject_motion,
            "camera_movement": camera_desc,
            "environment_motion": env_motion,
            "mood": f"{visual_style} — {shot.visual_style_note}",
            "duration_seconds": shot.duration_seconds,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "transition_to_next": shot.transition_to_next,
            "audio_direction": f"{audio_direction} [music_mood: {music_mood}]",
        }

        if image_prompt:
            video_prompt["reference_image_prompt_summary"] = image_prompt.get("image_prompt", {}).get("subject", "")

        provider_options: dict[str, Any] = {
            "seedance": _seedance_options(shot, shot.duration_seconds),
            "veo": _veo_options(shot, shot.duration_seconds),
            "runway": _runway_options(shot, shot.duration_seconds),
            "kling": _kling_options(shot, shot.duration_seconds),
        }

        return {
            "shot_index": shot.shot_index,
            "beat_type": shot.beat_type.value,
            "reference_image_role": "subject",
            "video_prompt": video_prompt,
            "provider_options": provider_options,
        }

    def build_all(
        self,
        shot_list: ShotList,
        image_prompts: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        img_map: dict[int, dict[str, Any]] = {}
        if image_prompts:
            for ip in image_prompts:
                img_map[ip["shot_index"]] = ip

        return [
            self.build(shot, img_map.get(shot.shot_index), context)
            for shot in shot_list.shots
        ]
