from __future__ import annotations

from typing import List, Tuple
from .schemas import DetectedBox, PlatformPreset, SafeZone
from .ui_detector import detect_ui_boxes


def compute_safe_zone(
    width: int,
    height: int,
    platform: PlatformPreset,
    frame_sample_paths: List[str],
    ui_detection_enabled: bool = True,
) -> SafeZone:
    blocked = detect_ui_boxes(frame_sample_paths, width, height, platform, ui_detection_enabled)
    candidates = _candidate_rects(width, height, platform)
    best = max(candidates, key=lambda item: _score_rect(item[1], blocked, width, height))
    placement, rect = best
    reason = "selected_rect_with_lowest_ui_overlap"
    return SafeZone(width=width, height=height, platform=platform, safe_rect=rect, blocked_boxes=blocked, placement=placement, reason=reason)


def _candidate_rects(width: int, height: int, platform: PlatformPreset):
    if platform in {PlatformPreset.tiktok, PlatformPreset.reels, PlatformPreset.shorts}:
        return [
            ("lower_third_left_safe", (int(width * 0.06), int(height * 0.66), int(width * 0.78), int(height * 0.82))),
            ("middle_center_safe", (int(width * 0.10), int(height * 0.45), int(width * 0.82), int(height * 0.60))),
            ("upper_third_center_safe", (int(width * 0.10), int(height * 0.18), int(width * 0.82), int(height * 0.32))),
        ]
    return [
        ("bottom_center", (int(width * 0.10), int(height * 0.74), int(width * 0.90), int(height * 0.90))),
        ("middle_center", (int(width * 0.16), int(height * 0.44), int(width * 0.84), int(height * 0.60))),
    ]


def _score_rect(rect: Tuple[int, int, int, int], blocked: List[DetectedBox], width: int, height: int) -> float:
    area = max(1, (rect[2] - rect[0]) * (rect[3] - rect[1]))
    overlap = sum(_intersection_area(rect, b.xyxy) / area for b in blocked)
    lower_bias = rect[1] / max(height, 1) * 0.12
    center_bias = 0.08 if rect[2] < int(width * 0.86) else 0
    return 1.0 - overlap + lower_bias + center_bias


def _intersection_area(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> int:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0
    return (x2 - x1) * (y2 - y1)
