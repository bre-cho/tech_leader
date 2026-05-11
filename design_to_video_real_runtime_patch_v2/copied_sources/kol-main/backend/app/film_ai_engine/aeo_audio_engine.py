from __future__ import annotations
from typing import List
from .schemas import ProjectBible, ShotBlock, AEOPlan

class AEOAudioEngine:
    """Builds pure-voice narration + 3-layer soundscape prompt plan."""
    def build(self, shot_blocks: List[ShotBlock], bible: ProjectBible) -> AEOPlan:
        narration_lines = [s.narrator_vo.strip() for s in shot_blocks if s.narrator_vo and s.narrator_vo.strip()]
        narration_text = "\n".join(narration_lines)
        return AEOPlan(
            voice_prompt=f"speech, cinematic narration, {bible.voice_direction}, clean voice only, no music baked into TTS",
            narration_text=narration_text,
            environment_layer=bible.soundscape_layers.get("environment", "subtle environment"),
            foley_layer=bible.soundscape_layers.get("foley", "tactile foley"),
            music_layer=bible.soundscape_layers.get("music", "minimal cinematic bed"),
            mix_policy={
                "environment_gain_pct": 50,
                "foley_gain_pct": 30,
                "music_gain_pct": 20,
                "sonic_restraint": True,
                "voice_ducking": True,
                "karaoke_from_clean_voice": True,
            },
        )
