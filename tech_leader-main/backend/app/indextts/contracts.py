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
    voice_reference_path: str
    output_dir: str
    emotion: EmotionVector = Field(default_factory=EmotionVector)
    language: str = "vi"
    seed: int = 42
    provider_mode: str = "real"
    model_dir: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


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
    job_id: str = "timeline_mix"


class TimelineMixResponse(BaseModel):
    status: str
    output_path: str
    artifact: Dict[str, Any]
