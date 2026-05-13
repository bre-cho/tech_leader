from __future__ import annotations

from app.video_postprocess.contracts import SafeZone, SubtitleLine, SubtitleStyle


def validate_subtitles(lines: list[SubtitleLine], style: SubtitleStyle, safe_zone: SafeZone) -> dict:
    checks = {
        "has_lines": len(lines) > 0,
        "line_length_safe": all(len(line.text) <= style.max_chars_per_line + 12 for line in lines),
        "timing_order_valid": all(line.end > line.start for line in lines),
        "safe_zone_exists": bool(safe_zone.safe_rect),
        "mobile_ui_aware": "ui" in safe_zone.reason or safe_zone.platform.value not in {"tiktok", "reels", "shorts"},
        "karaoke_words_present": all(len(line.words) > 0 for line in lines),
    }
    score = round(sum(1 for v in checks.values() if v) / len(checks) * 100, 2)
    return {
        "passed": score >= 90,
        "score": score,
        "checks": checks,
        "issues": [k for k, v in checks.items() if not v],
    }
