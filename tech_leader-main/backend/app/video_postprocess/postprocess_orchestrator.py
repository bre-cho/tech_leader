from __future__ import annotations

from pathlib import Path

from app.video_postprocess.audio_mix_service import RealAudioMixService
from app.video_postprocess.contracts import (
    SmartSubtitleRequest,
    VideoPostprocessRequest,
    VideoPostprocessResponse,
)
from app.video_postprocess.smart_karaoke_subtitle_service import SmartKaraokeSubtitleService
from app.video_postprocess.subtitle_burn_service import RealSubtitleBurnService


class VideoPostprocessOrchestrator:
    '''
    Correct runtime position in MVP:

    Storyboard Agent
    -> Render clips
    -> Merge clips / timeline
    -> TTS voiceover + word timestamps
    -> [HERE] Audio Mix Service
    -> [HERE] Smart Karaoke Subtitle Service
    -> [HERE] Subtitle Burn + Audio Mux
    -> Artifact Contract / 4K-8K Export / Promotion Gate

    This is postprocess runtime, not Storyboard Agent core.
    Storyboard Agent only passes scene script, body-language plan, CTA text and timing hints.
    '''

    def __init__(self):
        self.audio_mix = RealAudioMixService()
        self.subtitle = SmartKaraokeSubtitleService()
        self.burner = RealSubtitleBurnService()

    def run(self, req: VideoPostprocessRequest) -> VideoPostprocessResponse:
        out_dir = Path(req.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        subtitle_resp = self.subtitle.build(
            SmartSubtitleRequest(
                script=req.script,
                duration=req.duration,
                platform=req.platform,
                aspect_ratio=req.aspect_ratio,
                width=req.width,
                height=req.height,
                scene_emotion=req.scene_emotion,
                real_word_timestamps=req.word_timestamps,
            )
        )

        ass_path = out_dir / "subtitles_karaoke.ass"
        srt_path = out_dir / "subtitles.srt"
        ass_path.write_text(subtitle_resp.ass_text, encoding="utf-8")
        srt_path.write_text(subtitle_resp.srt_text, encoding="utf-8")

        mixed_audio_path = out_dir / "mixed_audio.aac"
        final_video_path = out_dir / "final_video_with_karaoke.mp4"

        if req.dry_run:
            return VideoPostprocessResponse(
                status="dry_run_ready",
                stage="subtitle_audio_mix_plan",
                mixed_audio_path=str(mixed_audio_path),
                ass_path=str(ass_path),
                srt_path=str(srt_path),
                final_video_path=str(final_video_path),
                subtitle_quality_gate=subtitle_resp.quality_gate,
                render_handoff={
                    **subtitle_resp.render_handoff,
                    "audio_mix_position": "after TTS, before subtitle burn",
                    "subtitle_position": "after word timing, before final mux",
                    "final_mux_position": "after clip merge and audio mix",
                },
            )

        mixed = self.audio_mix.mix(
            voice_path=req.voice_path,
            output_path=str(mixed_audio_path),
            bgm_path=req.bgm_path,
            sfx_paths=req.sfx_paths,
        )

        final = self.burner.burn(
            video_path=req.video_path,
            output_path=str(final_video_path),
            subtitle_path=str(ass_path) if req.burn_subtitles else None,
            audio_path=mixed,
        )

        return VideoPostprocessResponse(
            status="succeeded",
            stage="final_video_export",
            mixed_audio_path=mixed,
            ass_path=str(ass_path),
            srt_path=str(srt_path),
            final_video_path=final,
            subtitle_quality_gate=subtitle_resp.quality_gate,
            render_handoff=subtitle_resp.render_handoff,
        )
