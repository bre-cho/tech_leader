from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TrackType(str, Enum):
    dialogue = "dialogue"
    sfx = "sfx"
    ambience = "ambience"
    music = "music"


class TTSProvider(str, Enum):
    mock = "mock"
    indextts2 = "indextts2"
    external = "external"


class EmotionVector(BaseModel):
    # IndexTTS2 official order from Draft to Take docs:
    # joy, anger, sadness, fear, disgust, low_mood, surprise, calm
    joy: float = 0.0
    anger: float = 0.0
    sadness: float = 0.0
    fear: float = 0.0
    disgust: float = 0.0
    low_mood: float = 0.0
    surprise: float = 0.0
    calm: float = 0.0

    def clipped(self) -> "EmotionVector":
        data = self.model_dump()
        data = {k: min(max(float(v), 0.0), 0.5) for k, v in data.items()}
        total = sum(data.values())
        if total > 1.5:
            scale = 1.5 / total
            data = {k: round(v * scale, 4) for k, v in data.items()}
        return EmotionVector(**data)


class VoiceAsset(BaseModel):
    voice_id: str
    display_name: str
    source_wav_path: str
    language: str = "vi"
    tags: List[str] = Field(default_factory=list)
    prepared: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CharacterProfile(BaseModel):
    character_id: str
    display_name: str
    voice_id: str
    role: str = "speaker"
    default_emotion: EmotionVector = Field(default_factory=EmotionVector)
    speaking_style: str = "natural, clear, commercial"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScriptLine(BaseModel):
    line_id: str
    speaker_id: str
    text: str
    start_hint: Optional[float] = None
    duration_hint: Optional[float] = None
    emotion: EmotionVector = Field(default_factory=EmotionVector)
    manual_emotion: bool = False
    take_id: Optional[str] = None
    locked: bool = False


class SoundMarker(BaseModel):
    marker_id: str
    type: TrackType
    prompt: str
    start: float = 0.0
    duration: float = 2.0
    volume: float = 0.5


class ScriptCanvasProject(BaseModel):
    project_id: str
    title: str
    lines: List[ScriptLine] = Field(default_factory=list)
    sound_markers: List[SoundMarker] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineClip(BaseModel):
    clip_id: str
    track_type: TrackType
    source_id: str
    start: float
    end: float
    volume: float = 1.0
    locked: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Timeline(BaseModel):
    timeline_id: str
    project_id: str
    clips: List[TimelineClip]
    duration: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerateLineRequest(BaseModel):
    project_id: str
    line: ScriptLine
    character: CharacterProfile
    voice: VoiceAsset
    provider: TTSProvider = TTSProvider.mock
    regenerate: bool = False


class GeneratedTake(BaseModel):
    take_id: str
    line_id: str
    speaker_id: str
    audio_path: str
    duration: float
    emotion: EmotionVector
    provider: str
    locked: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineBuildRequest(BaseModel):
    project: ScriptCanvasProject
    takes: List[GeneratedTake]
    characters: List[CharacterProfile]
    voices: List[VoiceAsset]
    crossfade_ms: int = 80


class ExportMixRequest(BaseModel):
    timeline: Timeline
    output_path: str
    provider: TTSProvider = TTSProvider.mock
    target_lufs: float = -14.0


class StudioRunRequest(BaseModel):
    title: str = "Demo IndexTTS Studio Project"
    script: str
    brand_name: Optional[str] = None
    provider: TTSProvider = TTSProvider.mock
    default_voice_path: str = "/tmp/demo_voice.wav"
    export_dir: str = "/tmp/indextts-studio-demo"
    include_sfx_markers: bool = True


class StudioRunResponse(BaseModel):
    project: ScriptCanvasProject
    voices: List[VoiceAsset]
    characters: List[CharacterProfile]
    takes: List[GeneratedTake]
    timeline: Timeline
    export_mix_path: str
    handoff: Dict[str, Any]
