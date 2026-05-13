from __future__ import annotations

from pathlib import Path

from app.tts_studio.contracts import (
    ExportMixRequest,
    GenerateLineRequest,
    StudioRunRequest,
    StudioRunResponse,
    TimelineBuildRequest,
)
from app.tts_studio.export_mix import ExportMixService
from app.tts_studio.indextts_provider import IndexTTSProviderBoundary
from app.tts_studio.script_canvas import ScriptCanvasParser
from app.tts_studio.timeline import TimelineBuilder
from app.tts_studio.voice_studio import VoiceStudioService


class IndexTTSWorkflowStudioOrchestrator:
    '''
    Correct position in AI Creative OS:

    Storyboard Agent / Script Agent
    -> [HERE] Script Canvas + Speaker assignment
    -> [HERE] Voice Studio / Character Cast
    -> [HERE] IndexTTS2 line generation + regeneration
    -> [HERE] Embedded timeline
    -> Export mix
    -> LTX LipDub Runtime
    -> Karaoke Subtitle + Audio Mix Postprocess
    -> Final Video Export
    '''

    def __init__(self):
        self.voice_studio = VoiceStudioService()
        self.canvas = ScriptCanvasParser()
        self.tts = IndexTTSProviderBoundary()
        self.timeline = TimelineBuilder()
        self.exporter = ExportMixService()

    def run(self, req: StudioRunRequest) -> StudioRunResponse:
        out_dir = Path(req.export_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        voice = self.voice_studio.prepare_voice(
            display_name=f"{req.brand_name or 'Demo'} Voice",
            source_wav_path=req.default_voice_path,
        )
        character = self.voice_studio.create_character("Narrator", voice)

        project = self.canvas.parse(req.title, req.script, default_speaker_id=character.character_id)

        takes = []
        for line in project.lines:
            line.speaker_id = character.character_id
            take = self.tts.generate_line(
                GenerateLineRequest(
                    project_id=project.project_id,
                    line=line,
                    character=character,
                    voice=voice,
                    provider=req.provider,
                ),
                output_dir=str(out_dir / "takes"),
            )
            takes.append(take)

        timeline = self.timeline.build(
            TimelineBuildRequest(
                project=project,
                takes=takes,
                characters=[character],
                voices=[voice],
            )
        )

        mix_path = self.exporter.export(
            ExportMixRequest(
                timeline=timeline,
                output_path=str(out_dir / "export_mix.txt"),
                provider=req.provider,
            )
        )

        return StudioRunResponse(
            project=project,
            voices=[voice],
            characters=[character],
            takes=takes,
            timeline=timeline,
            export_mix_path=mix_path,
            handoff={
                "next": [
                    "LTX LipDub runtime: use exported voice/dialogue timing with source avatar video",
                    "KOL subtitle karaoke runtime: use project lines or word timestamps",
                    "Audio mix runtime: replace mock mix with FFmpeg final mix in production",
                ],
                "timeline_tracks": timeline.metadata.get("tracks", []),
                "memory_keys": ["voice_id", "character_id", "project_id", "take_id"],
            },
        )
