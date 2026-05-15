from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    retrying = "retrying"


class TTSProviderMode(str, Enum):
    indextts2 = "indextts2"
    supertonic = "supertonic"
    hybrid = "hybrid"
    dry_run = "dry_run"


class VoiceClonePolicy(str, Enum):
    strict_clone = "strict_clone"
    edge_fast_voice = "edge_fast_voice"
    hybrid_fallback = "hybrid_fallback"


class EmotionVector(BaseModel):
    joy: float = 0.0
    anger: float = 0.0
    sadness: float = 0.0
    fear: float = 0.0
    disgust: float = 0.0
    low_mood: float = 0.0
    surprise: float = 0.0
    calm: float = 0.0


class GenerateLineJobRequest(BaseModel):
    line_id: str
    speaker_id: str
    text: str
    voice_reference_path: Optional[str] = None
    output_dir: str
    emotion: EmotionVector = Field(default_factory=EmotionVector)
    language: str = "vi"
    seed: int = 42
    provider_mode: TTSProviderMode = TTSProviderMode.hybrid
    clone_policy: VoiceClonePolicy = VoiceClonePolicy.hybrid_fallback
    indextts_model_dir: Optional[str] = None
    supertonic_voice_name: str = "F1"
    supertonic_auto_download: bool = True
    enhancement: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)


class VoiceProfileRequest(BaseModel):
    profile_id: str
    display_name: str
    voice_reference_path: str
    output_dir: str
    preferred_provider: TTSProviderMode = TTSProviderMode.hybrid
    supertonic_voice_name: str = "F1"
    language: str = "vi"


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    attempts: int = 0
    max_attempts: int = 3
    request: GenerateLineJobRequest
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


class TimelineMixRequest(BaseModel):
    clips: List[Dict[str, Any]]
    output_path: str
    target_lufs: float = -14.0
    job_id: str = "voice_timeline_mix"


class TimelineMixResponse(BaseModel):
    status: str
    output_path: str
    artifact: Dict[str, Any]
