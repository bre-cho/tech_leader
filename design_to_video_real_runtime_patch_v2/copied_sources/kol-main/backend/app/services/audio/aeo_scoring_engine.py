"""aeo_scoring_engine — AEO-Aligned Scoring Engine (Giám đốc Âm nhạc - Phần 2).

Produces **per-segment music scoring briefs** — both lyrical and instrumental —
aligned to each story beat in the video.  The engine implements the
*AEO-Aligned Scoring Engine* pillar described in the Master Prompt architecture.

What it generates:

* ``music_brief`` — a structured music production brief for the segment, including:
    - ``mood``, ``tempo``, ``key_instruments``, ``intensity``
    - ``lyric_line`` (if lyrics are enabled and a line is appropriate)
    - ``mix_role`` — how this segment sits in the overall audio mix
    - ``provider_prompt`` — ready-to-use text prompt for a music-generation API
      (e.g. ElevenLabs, Suno, Udio, Mubert)

* ``voiceover_brief`` — direction for the TTS / VO artist for this segment.

The output of :meth:`AeoScoringEngine.score_all` is a list of
:class:`SegmentScore` objects — one per shot/beat — that the
:class:`~app.services.audio.audio_mix_service` can consume directly.

Usage::

    engine = AeoScoringEngine()
    scores = engine.score_all(shot_list, context=profile.to_context())
    for score in scores:
        print(score.shot_index, score.music_brief["provider_prompt"])
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.story_beat import BeatType
from app.services.strategy.shot_list_compiler import Shot, ShotList


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class MusicBrief(BaseModel):
    mood: str
    tempo: str
    bpm: int
    key_instruments: list[str]
    intensity: str
    mix_role: str
    provider_prompt: str
    lyric_line: str = ""
    force_instrumental: bool = True


class VoiceoverBrief(BaseModel):
    style: str
    pace: str
    breath_note: str
    emotional_direction: str


class SegmentScore(BaseModel):
    shot_index: int
    beat_type: BeatType
    duration_seconds: float
    music_brief: MusicBrief
    voiceover_brief: VoiceoverBrief


# ---------------------------------------------------------------------------
# Beat-level scoring tables
# ---------------------------------------------------------------------------

_MUSIC_TEMPLATES: dict[BeatType, dict[str, Any]] = {
    BeatType.hook: {
        "mood": "tense anticipation",
        "tempo": "slow build",
        "bpm_offset": -20,
        "key_instruments": ["low strings", "single piano note", "sub bass"],
        "intensity": "low_to_medium",
        "mix_role": "atmosphere_under_vo",
        "lyric_line_template": "",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "cinematic tension build, sparse arrangement, silence as instrument, "
            "no drums yet, {bpm} BPM"
        ),
    },
    BeatType.setup: {
        "mood": "warm authority",
        "tempo": "moderate",
        "bpm_offset": 0,
        "key_instruments": ["piano", "pad strings", "subtle percussion"],
        "intensity": "medium",
        "mix_role": "warm_underscore",
        "lyric_line_template": "",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "trustworthy and inspiring, building warmth, {bpm} BPM"
        ),
    },
    BeatType.escalation: {
        "mood": "building tension",
        "tempo": "increasing",
        "bpm_offset": 10,
        "key_instruments": ["tension strings", "driving percussion", "brass stabs"],
        "intensity": "medium_high",
        "mix_role": "tension_builder",
        "lyric_line_template": "{topic_hook}",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "escalating energy, rhythmic pulse, forward momentum, {bpm} BPM"
        ),
    },
    BeatType.conflict: {
        "mood": "confrontational power",
        "tempo": "slow deliberate",
        "bpm_offset": -15,
        "key_instruments": ["low brass", "minimal bass", "silence"],
        "intensity": "high",
        "mix_role": "power_statement",
        "lyric_line_template": "",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "cold authority, minimal arrangement, impact through restraint, {bpm} BPM"
        ),
    },
    BeatType.reveal: {
        "mood": "revelation swell",
        "tempo": "held breath then release",
        "bpm_offset": -5,
        "key_instruments": ["full strings", "piano", "choir pad"],
        "intensity": "peak",
        "mix_role": "emotional_peak",
        "lyric_line_template": "{reveal_truth}",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "emotional revelation, swell from silence, goosebump moment, {bpm} BPM"
        ),
    },
    BeatType.climax: {
        "mood": "epic peak",
        "tempo": "full energy",
        "bpm_offset": 15,
        "key_instruments": ["full orchestra", "epic percussion", "brass fanfare", "choir"],
        "intensity": "maximum",
        "mix_role": "climax_statement",
        "lyric_line_template": "{mission_line}",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "cinematic epic peak, full orchestral power, transformational energy, {bpm} BPM"
        ),
    },
    BeatType.resolution: {
        "mood": "triumphant resolve",
        "tempo": "settling",
        "bpm_offset": -10,
        "key_instruments": ["warm strings", "piano melody", "gentle pad"],
        "intensity": "medium",
        "mix_role": "resolution_warmth",
        "lyric_line_template": "",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "resolution and relief, warm harmonic resolution, earned satisfaction, {bpm} BPM"
        ),
    },
    BeatType.cta: {
        "mood": "energetic invitation",
        "tempo": "upbeat bright",
        "bpm_offset": 20,
        "key_instruments": ["bright piano", "light percussion", "uplifting synth"],
        "intensity": "medium_high",
        "mix_role": "action_motivator",
        "lyric_line_template": "{cta_phrase}",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "motivating call to action, positive energy, memorable hook, {bpm} BPM"
        ),
    },
    BeatType.callback: {
        "mood": "echo of origin",
        "tempo": "echo of hook",
        "bpm_offset": -20,
        "key_instruments": ["single piano note", "low strings"],
        "intensity": "low",
        "mix_role": "emotional_callback",
        "lyric_line_template": "",
        "provider_prompt_template": (
            "{mood} {music_mood} music, {tempo}, {key_instruments}, "
            "callback to opening theme, resolved version of hook motif, {bpm} BPM"
        ),
    },
}

_VO_TEMPLATES: dict[BeatType, dict[str, str]] = {
    BeatType.hook: {
        "pace": "slow_then_accelerate",
        "breath_note": "audible inhale before line",
        "emotional_direction": "controlled intensity — challenge the viewer",
    },
    BeatType.setup: {
        "pace": "moderate_measured",
        "breath_note": "natural breathing, warm tone",
        "emotional_direction": "authoritative and welcoming",
    },
    BeatType.escalation: {
        "pace": "building_faster",
        "breath_note": "tight breath, energy building",
        "emotional_direction": "urgency and conviction",
    },
    BeatType.conflict: {
        "pace": "slow_deliberate",
        "breath_note": "controlled breath, cold delivery",
        "emotional_direction": "cold authority — state facts, not emotion",
    },
    BeatType.reveal: {
        "pace": "pause_then_deliver",
        "breath_note": "long pause before the key phrase",
        "emotional_direction": "restrained urgency — let the truth land",
    },
    BeatType.climax: {
        "pace": "peak_intensity",
        "breath_note": "full breath support for maximum impact",
        "emotional_direction": "raw conviction — nothing held back",
    },
    BeatType.resolution: {
        "pace": "slower_settling",
        "breath_note": "audible exhale of relief",
        "emotional_direction": "warm satisfaction — the mission complete",
    },
    BeatType.cta: {
        "pace": "energetic_direct",
        "breath_note": "bright open tone, forward energy",
        "emotional_direction": "inviting action — friend giving advice",
    },
    BeatType.callback: {
        "pace": "mirroring_hook",
        "breath_note": "echo of hook breath pattern",
        "emotional_direction": "completion — the circle closes",
    },
}


# ---------------------------------------------------------------------------
# Lyric-line context helpers
# ---------------------------------------------------------------------------

def _build_lyric_context(beat_type: BeatType, ctx: dict[str, Any]) -> dict[str, str]:
    topic = ctx.get("topic", "")
    mission = ctx.get("mission", "")
    uvp = ctx.get("unique_value_proposition", "")
    return {
        "topic_hook": topic[:60] if topic else "",
        "reveal_truth": uvp[:60] if uvp else "",
        "mission_line": mission[:60] if mission else "",
        "cta_phrase": ctx.get("signature_phrases", [""])[0] if ctx.get("signature_phrases") else "",
    }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class AeoScoringEngine:
    """Generate per-segment AEO-aligned music and VO scoring briefs.

    Context keys consumed (from ``ProjectProfile.to_context()``):
        music_mood (str): Overarching mood label (e.g. "epic motivational").
        bpm_range (tuple[int, int]): Min/max BPM for the project.
        preferred_instruments (list[str]): Global instrument preferences.
        voiceover_style (str): Global VO style (e.g. "authoritative").
        breath_pacing_preset (str): Global breath-pacing preset.
        lyrics_enabled (bool): Whether lyric lines should be populated.
        mission (str): Project mission (used in lyric context).
        unique_value_proposition (str): UVP (used in lyric context).
        signature_phrases (list[str]): Recurring phrases.
    """

    def score(self, shot: Shot, context: dict[str, Any] | None = None) -> SegmentScore:
        ctx = context or {}
        music_mood = ctx.get("music_mood", "epic motivational")
        bpm_range: tuple[int, int] = tuple(ctx.get("bpm_range", (90, 130)))  # type: ignore[assignment]
        preferred_instruments = ctx.get("preferred_instruments", [])
        voiceover_style = ctx.get("voiceover_style", "authoritative")
        breath_pacing_preset = ctx.get("breath_pacing_preset", "dramatic")
        lyrics_enabled = bool(ctx.get("lyrics_enabled", False))

        tmpl = _MUSIC_TEMPLATES.get(shot.beat_type, _MUSIC_TEMPLATES[BeatType.setup])
        vo_tmpl = _VO_TEMPLATES.get(shot.beat_type, _VO_TEMPLATES[BeatType.setup])

        # Calculate BPM within project range
        bpm_mid = (bpm_range[0] + bpm_range[1]) // 2
        bpm = max(bpm_range[0], min(bpm_range[1], bpm_mid + tmpl["bpm_offset"]))

        # Merge project instruments with beat instruments
        beat_instruments = list(tmpl["key_instruments"])
        for instr in preferred_instruments:
            if instr not in beat_instruments:
                beat_instruments.append(instr)

        # Build provider prompt
        instruments_str = ", ".join(beat_instruments[:4])
        provider_prompt = tmpl["provider_prompt_template"].format(
            mood=tmpl["mood"],
            music_mood=music_mood,
            tempo=tmpl["tempo"],
            key_instruments=instruments_str,
            bpm=bpm,
        )

        # Build lyric line (only if lyrics enabled)
        lyric_line = ""
        if lyrics_enabled and tmpl["lyric_line_template"]:
            lyric_ctx = _build_lyric_context(shot.beat_type, ctx)
            lyric_line = tmpl["lyric_line_template"].format(**lyric_ctx)

        music_brief = MusicBrief(
            mood=tmpl["mood"],
            tempo=tmpl["tempo"],
            bpm=bpm,
            key_instruments=beat_instruments[:5],
            intensity=tmpl["intensity"],
            mix_role=tmpl["mix_role"],
            provider_prompt=provider_prompt,
            lyric_line=lyric_line,
            force_instrumental=not lyrics_enabled,
        )

        voiceover_brief = VoiceoverBrief(
            style=voiceover_style,
            pace=vo_tmpl["pace"],
            breath_note=vo_tmpl["breath_note"],
            emotional_direction=vo_tmpl["emotional_direction"],
        )

        # Carry topic into context for lyric rendering if not already present
        if "topic" not in ctx:
            ctx = {**ctx, "topic": shot.visual_style_note}

        return SegmentScore(
            shot_index=shot.shot_index,
            beat_type=shot.beat_type,
            duration_seconds=shot.duration_seconds,
            music_brief=music_brief,
            voiceover_brief=voiceover_brief,
        )

    def score_all(
        self,
        shot_list: ShotList,
        context: dict[str, Any] | None = None,
    ) -> list[SegmentScore]:
        ctx = dict(context or {})
        if "topic" not in ctx:
            ctx["topic"] = shot_list.topic
        return [self.score(shot, ctx) for shot in shot_list.shots]
