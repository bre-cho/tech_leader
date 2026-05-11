from __future__ import annotations

from typing import Dict, List
from .schemas import SafeZone, SubtitleLine, SubtitleStyle


def validate_subtitles(lines: List[SubtitleLine], style: SubtitleStyle, safe_zone: SafeZone) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []
    if not lines:
        errors.append("NO_SUBTITLE_LINES")
    for line in lines:
        if line.end <= line.start:
            errors.append(f"INVALID_TIMING:{line.line_id}")
        if len(line.text) > style.max_chars_per_line * 2:
            warnings.append(f"LONG_LINE:{line.line_id}")
    x1, y1, x2, y2 = safe_zone.safe_rect
    if x1 < 0 or y1 < 0 or x2 > safe_zone.width or y2 > safe_zone.height:
        errors.append("SAFE_ZONE_OUT_OF_FRAME")
    if any(box.label.endswith("right_action_stack") and safe_zone.placement == "bottom_center" for box in safe_zone.blocked_boxes):
        warnings.append("PLATFORM_UI_PRESENT_USE_LEFT_SAFE_ZONE")
    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "rules": [
            "NO_VOICE_NO_SUBTITLE",
            "NO_SAFE_ZONE_NO_BURN_IN",
            "NO_STYLE_NO_EXPORT",
            "NO_KARAOKE_TIMING_NO_ASS",
        ],
    }
