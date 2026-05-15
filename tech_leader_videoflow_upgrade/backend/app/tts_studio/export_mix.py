from __future__ import annotations

from pathlib import Path

from app.tts_studio.contracts import ExportMixRequest


class ExportMixService:
    '''
    Mix export handoff.

    In mock mode: writes timeline manifest.
    In production: can call FFmpeg or the existing KOL audio_mix_service.
    '''

    def export(self, req: ExportMixRequest) -> str:
        out = Path(req.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if req.provider.value == "mock":
            out.write_text(
                "MOCK MIX EXPORT\n"
                f"target_lufs={req.target_lufs}\n"
                f"duration={req.timeline.duration}\n"
                f"clips={len(req.timeline.clips)}\n"
                + req.timeline.model_dump_json(indent=2),
                encoding="utf-8",
            )
            return str(out)

        payload = {
            "timeline": req.timeline.model_dump(),
            "output_path": str(out),
            "target_lufs": req.target_lufs,
            "next_runtime": "kol_subtitle_karaoke_audio_mix_mvp_patch.audio_mix_service",
        }
        out.with_suffix(".json").write_text(str(payload), encoding="utf-8")
        return str(out.with_suffix(".json"))
