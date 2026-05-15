from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
class LipDubMode(str, Enum): comfyui='comfyui'; ltx_pipeline='ltx_pipeline'; mock='mock'
class LipDubQuality(str, Enum): preview='preview'; production='production'; high_quality='high_quality'
class LipDubRequest(BaseModel):
    source_video_path: str; dialogue_text: str; output_dir: str
    mode: LipDubMode = LipDubMode.mock; quality: LipDubQuality = LipDubQuality.production
    speaker_voice_reference_path: Optional[str] = None; audio_prompt: Optional[str] = None
    preserve_identity: bool = True; preserve_background: bool = True; preserve_delivery_tone: bool = True
    face_region_strength: float = 0.82; ic_lora_strength: float = 0.85; seed: int = 42
    brand_name: Optional[str] = None; avatar_id: Optional[str] = None; campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict); save_memory: bool = True
class LipDubArtifact(BaseModel):
    artifact_id: str; artifact_type: str; path_or_url: str; provider: str; checksum: str; metadata: Dict[str, Any] = Field(default_factory=dict)
class LipDubResponse(BaseModel):
    status: str; run_id: str; mode: LipDubMode; stage: str; recalled_context: str; provider_payload: Dict[str, Any]
    artifacts: List[LipDubArtifact] = Field(default_factory=list); qa_report: Dict[str, Any]; memory_update: Dict[str, Any]
