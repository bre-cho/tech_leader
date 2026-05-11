from __future__ import annotations

from .ass_writer import build_ass
from .quality_gate import validate_subtitles
from .safe_zone_engine import compute_safe_zone
from .schemas import SmartSubtitleRequest, SmartSubtitleResponse
from .srt_writer import build_srt
from .style_engine import choose_subtitle_style
from .timing_engine import build_subtitle_lines


class SmartSubtitleService:
    """P17 production subtitle layer: timing + style + safe-zone + UI avoidance."""

    def build(self, req: SmartSubtitleRequest) -> SmartSubtitleResponse:
        style = choose_subtitle_style(req.scene_emotion, req.platform, req.aspect_ratio)
        safe_zone = compute_safe_zone(
            width=req.width,
            height=req.height,
            platform=req.platform,
            frame_sample_paths=req.frame_sample_paths,
            ui_detection_enabled=req.ui_detection_enabled,
        )
        lines = build_subtitle_lines(
            script=req.script,
            duration=req.duration,
            max_chars=style.max_chars_per_line,
            scene_id=req.scene_id,
            emotion=req.scene_emotion,
            real_word_timestamps=req.real_word_timestamps,
        )
        ass_text = build_ass(lines, style, safe_zone)
        srt_text = build_srt(lines)
        gate = validate_subtitles(lines, style, safe_zone)
        return SmartSubtitleResponse(
            platform=req.platform,
            safe_zone=safe_zone,
            style=style,
            subtitle_lines=lines,
            ass_text=ass_text,
            srt_text=srt_text,
            quality_gate=gate,
            render_handoff={
                "burn_filter": "ass=path/to/subtitles.ass",
                "sidecar_formats": ["ass", "srt"],
                "safe_zone_placement": safe_zone.placement,
                "ffmpeg_example": "ffmpeg -i input.mp4 -vf ass=subtitles.ass -c:a copy output.mp4",
            },
        )
