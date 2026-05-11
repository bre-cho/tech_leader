from __future__ import annotations

from typing import List
from .schemas import SafeZone, SubtitleLine, SubtitleStyle


def seconds_to_ass_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def build_ass(subtitle_lines: List[SubtitleLine], style: SubtitleStyle, safe_zone: SafeZone) -> str:
    x1, y1, x2, y2 = safe_zone.safe_rect
    style.margin_l = max(24, x1)
    style.margin_r = max(24, safe_zone.width - x2)
    style.margin_v = max(24, safe_zone.height - y2)
    style.alignment = 2 if "lower" in safe_zone.placement or "bottom" in safe_zone.placement else 5

    header = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: {safe_zone.width}\nPlayResY: {safe_zone.height}\nScaledBorderAndShadow: yes\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: P17Smart,{style.font_family},{style.font_size},{style.primary_color},{style.secondary_color},{style.outline_color},{style.back_color},{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline},{style.shadow},{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
    events = []
    for line in subtitle_lines:
        events.append(
            f"Dialogue: 0,{seconds_to_ass_time(line.start)},{seconds_to_ass_time(line.end)},P17Smart,,0,0,0,,{_line_to_karaoke(line, style)}"
        )
    return header + "\n".join(events) + "\n"


def _line_to_karaoke(line: SubtitleLine, style: SubtitleStyle) -> str:
    if not line.words:
        return _escape_ass(line.text)
    pieces = []
    keywords = {k.lower() for k in line.keywords}
    for wt in line.words:
        dur_cs = max(1, int(round((wt.end - wt.start) * 100)))
        clean = wt.word.strip(".,!?;:()[]{}\"'").lower()
        word = wt.word.upper() if style.uppercase_keywords and (wt.emphasis or clean in keywords) else wt.word
        if style.karaoke_highlight and (wt.emphasis or clean in keywords):
            pieces.append(f"{{\\k{dur_cs}\\c{style.secondary_color}}}{_escape_ass(word)}{{\\c{style.primary_color}}}")
        else:
            pieces.append(f"{{\\k{dur_cs}}}{_escape_ass(word)}")
    return " ".join(pieces)


def _escape_ass(text: str) -> str:
    return (text or "").replace("{", "").replace("}", "").replace("\n", "\\N")
