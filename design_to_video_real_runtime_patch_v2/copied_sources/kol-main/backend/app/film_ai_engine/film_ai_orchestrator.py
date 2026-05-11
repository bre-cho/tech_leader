from __future__ import annotations
from typing import Any, Dict, List
from .project_bible_engine import ProjectBibleEngine
from .micro_saga_engine import MicroSagaEngine
from .cinematic_director_engine import CinematicDirectorEngine
from .aeo_audio_engine import AEOAudioEngine
from .quality_engine import FilmAIQualityEngine

class FilmAIOrchestrator:
    def __init__(self):
        self.bible_engine = ProjectBibleEngine()
        self.saga_engine = MicroSagaEngine()
        self.director = CinematicDirectorEngine()
        self.audio = AEOAudioEngine()
        self.qa = FilmAIQualityEngine()

    def upgrade_render_package(self, package: Dict[str, Any], campaign_brief: Dict[str, Any] | None = None, poster_analysis: Dict[str, Any] | None = None, providers: List[str] | None = None) -> Dict[str, Any]:
        campaign_brief = campaign_brief or package.get("storyboard_response", {}).get("input", {}).get("campaign_brief", {}) or {}
        bible = self.bible_engine.build(campaign_brief, poster_analysis)
        shot_blocks = self.saga_engine.build_shot_blocks(package, bible)
        director_output = self.director.compile(shot_blocks, bible, providers=providers)
        aeo_plan = self.audio.build(shot_blocks, bible)
        enriched = {
            **package,
            "pipeline": "poster_to_video_render_v2_film_ai_k01_26",
            "project_bible": bible.model_dump(),
            "film_ai_shot_blocks": [s.model_dump() for s in shot_blocks],
            "film_ai_director": director_output.model_dump(),
            "aeo_audio_plan": aeo_plan.model_dump(),
            "karaoke_subtitle_plan": {
                "mode": "word_level_ass",
                "source": "clean voice narration or TTS timestamps",
                "safe_zone": "visual aware placement; avoid platform UI",
                "burn_policy": "burn after final audio mix unless exporting clean master",
            },
        }
        enriched["film_ai_quality_gate"] = self.qa.score(enriched)
        return enriched
