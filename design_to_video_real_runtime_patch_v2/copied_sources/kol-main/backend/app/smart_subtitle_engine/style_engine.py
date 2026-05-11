from __future__ import annotations

from .schemas import PlatformPreset, SubtitleIntensity, SubtitleStyle


def choose_subtitle_style(
    emotion: SubtitleIntensity,
    platform: PlatformPreset,
    aspect_ratio: str = "9:16",
) -> SubtitleStyle:
    style = SubtitleStyle(style_id=f"{platform.value}_{emotion.value}")

    if platform in {PlatformPreset.tiktok, PlatformPreset.reels, PlatformPreset.shorts}:
        style.font_size = 66
        style.margin_l = 96
        style.margin_r = 96
        style.margin_v = 300
        style.max_chars_per_line = 24
    elif aspect_ratio == "16:9" or platform == PlatformPreset.youtube_16x9:
        style.font_size = 48
        style.margin_v = 92
        style.max_chars_per_line = 42

    if emotion == SubtitleIntensity.luxury:
        style.font_family = "Playfair Display"
        style.font_size = max(54, style.font_size - 6)
        style.primary_color = "&H00F7F1E8"
        style.secondary_color = "&H0038D5FF"
        style.outline = 4
        style.shadow = 3
    elif emotion == SubtitleIntensity.viral:
        style.font_family = "Montserrat ExtraBold"
        style.font_size += 8
        style.secondary_color = "&H0000F5FF"
        style.outline = 7
    elif emotion == SubtitleIntensity.dramatic:
        style.font_family = "Bebas Neue"
        style.primary_color = "&H00FFFFFF"
        style.secondary_color = "&H002E2EFF"
        style.outline = 6
    elif emotion == SubtitleIntensity.asmr:
        style.font_family = "Inter"
        style.font_size = max(44, style.font_size - 14)
        style.primary_color = "&H00EDEDED"
        style.secondary_color = "&H00D0D0D0"
        style.outline = 3
        style.shadow = 1
    elif emotion == SubtitleIntensity.documentary:
        style.font_family = "Source Sans 3"
        style.font_size = max(50, style.font_size - 8)
        style.primary_color = "&H00FFFFFF"
        style.secondary_color = "&H00C8E0FF"
    return style
