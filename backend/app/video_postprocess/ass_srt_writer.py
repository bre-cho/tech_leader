from __future__ import annotations

from app.video_postprocess.contracts import SafeZone, SubtitleLine, SubtitleStyle


def ass_time(seconds: float) -> str:
    seconds = max(seconds, 0.0)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(seconds: float) -> str:
    seconds = max(seconds, 0.0)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_ass(lines: list[SubtitleLine], style: SubtitleStyle, safe_zone: SafeZone) -> str:
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {safe_zone.width}\n"
        f"PlayResY: {safe_zone.height}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{style.font_family},{style.font_size},{style.primary_color},{style.secondary_color},"
        f"{style.outline_color},{style.back_color},{1 if style.bold else 0},0,0,0,100,100,0,0,1,"
        f"{style.outline},{style.shadow},{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    events = []
    for line in lines:
        text = _karaoke_text(line) if style.karaoke_highlight else line.text
        events.append(f"Dialogue: 0,{ass_time(line.start)},{ass_time(line.end)},Default,,0,0,0,,{text}")
    return header + "\n".join(events)


def _karaoke_text(line: SubtitleLine) -> str:
    parts = []
    for w in line.words:
        dur_cs = max(int((w.end - w.start) * 100), 5)
        word = w.word.upper() if w.emphasis else w.word
        parts.append(f"{{\\k{dur_cs}}}{word}")
    return " ".join(parts)


def build_srt(lines: list[SubtitleLine]) -> str:
    blocks = []
    for i, line in enumerate(lines, start=1):
        blocks.append(f"{i}\n{srt_time(line.start)} --> {srt_time(line.end)}\n{line.text}")
    return "\n\n".join(blocks) + "\n"
