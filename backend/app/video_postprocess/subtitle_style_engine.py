from __future__ import annotations

from app.video_postprocess.contracts import PlatformPreset, SubtitleEmotion, SubtitleStyle


def choose_subtitle_style(
    emotion: SubtitleEmotion,
    platform: PlatformPreset,
    aspect_ratio: str = "9:16",
) -> SubtitleStyle:
    mobile = platform in {PlatformPreset.tiktok, PlatformPreset.reels, PlatformPreset.shorts}
    base_size = 64 if mobile else 46
    margin_v = 300 if mobile else 80
    max_chars = 24 if mobile else 42

    if emotion == SubtitleEmotion.viral:
        return SubtitleStyle(
            style_id="viral_karaoke",
            font_family="Arial",
            font_size=base_size + 6,
            secondary_color="&H0000FFFF",
            outline=6,
            shadow=3,
            margin_v=margin_v,
            max_chars_per_line=max_chars,
            max_words_per_line=5,
        )

    if emotion == SubtitleEmotion.luxury:
        return SubtitleStyle(
            style_id="luxury_clean_karaoke",
            font_family="Arial",
            font_size=base_size,
            secondary_color="&H0060FFFF",
            outline=4,
            shadow=2,
            margin_v=margin_v,
            max_chars_per_line=max_chars,
            max_words_per_line=6,
        )

    if emotion == SubtitleEmotion.asmr:
        return SubtitleStyle(
            style_id="asmr_soft",
            font_family="Arial",
            font_size=base_size - 6,
            secondary_color="&H00D7B56D",
            outline=3,
            shadow=1,
            margin_v=margin_v,
            max_chars_per_line=max_chars + 4,
            max_words_per_line=7,
        )

    return SubtitleStyle(
        style_id=f"{emotion.value}_karaoke",
        font_family="Arial",
        font_size=base_size,
        margin_v=margin_v,
        max_chars_per_line=max_chars,
        max_words_per_line=6,
    )
