from __future__ import annotations

from app.video_postprocess.contracts import PlatformPreset, SafeZone


def compute_safe_zone(
    *,
    width: int,
    height: int,
    platform: PlatformPreset,
    frame_sample_paths: list[str] | None = None,
    ui_detection_enabled: bool = True,
) -> SafeZone:
    '''
    MVP safe-zone engine adapted from kol-main-4 smart subtitle engine.

    For TikTok/Reels/Shorts:
    - avoids top profile UI
    - avoids right action rail
    - avoids bottom caption/action area
    '''
    if platform in {PlatformPreset.tiktok, PlatformPreset.reels, PlatformPreset.shorts}:
        left = int(width * 0.08)
        top = int(height * 0.16)
        right = int(width * 0.84)
        bottom = int(height * 0.74)
        return SafeZone(
            width=width,
            height=height,
            platform=platform,
            safe_rect=(left, top, right, bottom),
            placement="bottom_center_above_ui",
            reason="mobile short-video safe zone; avoids right rail and bottom UI",
        )

    return SafeZone(
        width=width,
        height=height,
        platform=platform,
        safe_rect=(int(width * 0.08), int(height * 0.10), int(width * 0.92), int(height * 0.86)),
        placement="bottom_center",
        reason="generic broadcast-safe zone",
    )
