from __future__ import annotations

from pathlib import Path
from typing import List
from .schemas import DetectedBox, PlatformPreset


def detect_ui_boxes(
    frame_sample_paths: List[str],
    width: int,
    height: int,
    platform: PlatformPreset,
    enabled: bool = True,
) -> List[DetectedBox]:
    """Detect occupied UI/subject regions.

    Production behavior:
    - If ultralytics YOLO is installed and a frame exists, use it for person/object boxes.
    - Always add platform UI heuristic boxes for TikTok/Reels/Shorts because export UI is predictable.
    - If OpenCV is unavailable, the function remains deterministic and safe.
    """
    boxes: List[DetectedBox] = []
    if platform in {PlatformPreset.tiktok, PlatformPreset.reels, PlatformPreset.shorts}:
        boxes.extend(_mobile_platform_ui(width, height, platform))
    if not enabled:
        return boxes

    boxes.extend(_optional_yolo_boxes(frame_sample_paths, width, height))
    return _dedupe_boxes(boxes)


def _mobile_platform_ui(width: int, height: int, platform: PlatformPreset) -> List[DetectedBox]:
    right_w = int(width * 0.18)
    bottom_h = int(height * 0.16)
    top_h = int(height * 0.08)
    return [
        DetectedBox(label=f"{platform.value}_right_action_stack", confidence=0.99, xyxy=(width - right_w, int(height * 0.34), width, int(height * 0.88))),
        DetectedBox(label=f"{platform.value}_bottom_caption_ui", confidence=0.98, xyxy=(0, height - bottom_h, width, height)),
        DetectedBox(label=f"{platform.value}_top_status_ui", confidence=0.92, xyxy=(0, 0, width, top_h)),
    ]


def _optional_yolo_boxes(frame_sample_paths: List[str], width: int, height: int) -> List[DetectedBox]:
    if not frame_sample_paths:
        return []
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception:
        return []

    model_name = "yolov8n.pt"
    boxes: List[DetectedBox] = []
    try:
        model = YOLO(model_name)
        for path in frame_sample_paths[:3]:
            if not Path(path).exists():
                continue
            results = model(path, verbose=False)
            for res in results:
                names = getattr(res, "names", {}) or {}
                for b in getattr(res, "boxes", []) or []:
                    xyxy = b.xyxy[0].tolist()
                    conf = float(b.conf[0])
                    cls = int(b.cls[0])
                    if conf < 0.35:
                        continue
                    label = names.get(cls, "object")
                    boxes.append(
                        DetectedBox(
                            label=f"yolo_{label}",
                            confidence=round(conf, 3),
                            xyxy=(int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                            source="yolo",
                        )
                    )
    except Exception:
        return []
    return boxes


def _dedupe_boxes(boxes: List[DetectedBox]) -> List[DetectedBox]:
    seen = set()
    result: List[DetectedBox] = []
    for box in boxes:
        key = (box.label, box.xyxy)
        if key not in seen:
            result.append(box)
            seen.add(key)
    return result
