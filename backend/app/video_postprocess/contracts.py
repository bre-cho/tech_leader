from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple
from pydantic import BaseModel, Field


class PlatformPreset(str, Enum):
    tiktok = "tiktok"
    reels = "reels"
    shorts = "shorts"
    youtube_16x9 = "youtube_16x9"
    generic = "generic"


class SubtitleEmotion(str, Enum):
    calm = "calm"
    luxury = "luxury"
    dramatic = "dramatic"
    viral = "viral"
    documentary = "documentary"
    asmr = "asmr"


class WordTiming(BaseModel):
    word: str
    start: float
    end: float
    confidence: float = 0.85
    emphasis: bool = False


class SubtitleLine(BaseModel):
    line_id: str
    text: str
    start: float
    end: float
    words: List[WordTiming] = Field(default_factory=list)
    scene_id: Optional[str] = None
    emotion: SubtitleEmotion = SubtitleEmotion.luxury
    keywords: List[str] = Field(default_factory=list)


class DetectedBox(BaseModel):
    label: str
    confidence: float
    xyxy: Tuple[int, int, int, int]
    source: str = "heuristic"


class SafeZone(BaseModel):
    width: int
    height: int
    platform: PlatformPreset
    safe_rect: Tuple[int, int, int, int]
    blocked_boxes: List[DetectedBox] = Field(default_factory=list)
    placement: str = "bottom_center"
    reason: str = "default_mobile_safe_zone"


class SubtitleStyle(BaseModel):
    style_id: str
    font_family: str = "Arial"
    font_size: int = 64
    primary_color: str = "&H00FFFFFF"
    secondary_color: str = "&H0060FFFF"
    outline_color: str = "&H00141414"
    back_color: str = "&H80000000"
    bold: bool = True
    outline: int = 5
    shadow: int = 2
    alignment: int = 2
    margin_l: int = 96
    margin_r: int = 96
    margin_v: int = 280
    max_chars_per_line: int = 26
    max_words_per_line: int = 6
    uppercase_keywords: bool = True
    karaoke_highlight: bool = True


class SmartSubtitleRequest(BaseModel):
    script: str
    duration: float = 15.0
    platform: PlatformPreset = PlatformPreset.tiktok
    aspect_ratio: str = "9:16"
    width: int = 1080
    height: int = 1920
    scene_id: Optional[str] = None
    scene_emotion: SubtitleEmotion = SubtitleEmotion.luxury
    frame_sample_paths: List[str] = Field(default_factory=list)
    ui_detection_enabled: bool = True
    real_word_timestamps: Optional[List[WordTiming]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SmartSubtitleResponse(BaseModel):
    engine: str = "KOL_SMART_KARAOKE_SUBTITLE_ENGINE"
    platform: PlatformPreset
    safe_zone: SafeZone
    style: SubtitleStyle
    subtitle_lines: List[SubtitleLine]
    ass_text: str
    srt_text: str
    quality_gate: Dict[str, Any]
    render_handoff: Dict[str, Any]


class AudioMixRequest(BaseModel):
    voice_path: str
    output_path: str
    bgm_path: Optional[str] = None
    sfx_paths: List[str] = Field(default_factory=list)
    target_lufs: float = -14.0
    bgm_volume: float = 0.18
    sfx_volume: float = 0.55


class VideoPostprocessRequest(BaseModel):
    video_path: str
    voice_path: str
    output_dir: str
    script: str
    duration: float
    platform: PlatformPreset = PlatformPreset.tiktok
    aspect_ratio: str = "9:16"
    width: int = 1080
    height: int = 1920
    bgm_path: Optional[str] = None
    sfx_paths: List[str] = Field(default_factory=list)
    word_timestamps: Optional[List[WordTiming]] = None
    scene_emotion: SubtitleEmotion = SubtitleEmotion.luxury
    burn_subtitles: bool = True
    dry_run: bool = False


class VideoPostprocessResponse(BaseModel):
    status: str
    stage: str
    mixed_audio_path: Optional[str] = None
    ass_path: Optional[str] = None
    srt_path: Optional[str] = None
    final_video_path: Optional[str] = None
    subtitle_quality_gate: Optional[Dict[str, Any]] = None
    ffmpeg_required: bool = True
    render_handoff: Dict[str, Any] = Field(default_factory=dict)
