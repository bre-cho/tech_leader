
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

AspectRatio = Literal["1:1", "4:5", "3:4", "9:16", "16:9"]
RenderTier = Literal["draft", "premium", "hero"]
CommercialUseCase = Literal[
    "beauty_ad", "fashion_editorial", "cosmetic_product", "luxury_perfume",
    "poster", "ecommerce", "showroom", "beauty_avatar", "storyboard_keyframe"
]
ProviderMode = Literal["mock", "hf_inference", "local_diffusers"]

class HiDreamGenerateRequest(BaseModel):
    business_goal: str = Field(..., min_length=3)
    industry: str = Field(..., min_length=2)
    product_name: str = Field(..., min_length=1)
    audience: str = Field(default="premium buyers")
    use_case: CommercialUseCase = "poster"
    brand_dna: Dict[str, Any] = Field(default_factory=dict)
    visual_dna: Dict[str, Any] = Field(default_factory=dict)
    campaign_context: Dict[str, Any] = Field(default_factory=dict)
    copy_text: Optional[str] = None
    aspect_ratio: AspectRatio = "4:5"
    render_tier: RenderTier = "premium"
    seed: Optional[int] = None
    provider: Optional[ProviderMode] = None
    enable_typography_safe_mode: bool = True
    enable_storyboard_expansion: bool = True
    enable_8k_export_contract: bool = True

class HiDreamPromptContract(BaseModel):
    positive_prompt: str
    negative_prompt: str
    camera_grammar: Dict[str, Any]
    lighting_logic: Dict[str, Any]
    material_logic: Dict[str, Any]
    composition_logic: Dict[str, Any]
    typography_policy: Dict[str, Any]
    provider_params: Dict[str, Any]

class HiDreamScore(BaseModel):
    commercial_score: float
    luxury_score: float
    texture_score: float
    typography_score: float
    prompt_adherence_score: float
    storyboard_readiness_score: float
    winner_candidate: bool
    reasons: List[str]

class HiDreamArtifact(BaseModel):
    artifact_id: str
    artifact_type: str
    path: str
    url: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    provider: str
    model_id: str
    seed: Optional[int]
    replay_contract: Dict[str, Any]

class HiDreamGenerateResponse(BaseModel):
    status: Literal["ok", "blocked", "failed"]
    workflow_trace: List[str]
    prompt_contract: HiDreamPromptContract
    artifact: Optional[HiDreamArtifact]
    score: HiDreamScore
    storyboard_expansion: Dict[str, Any]
    promotion_gate: Dict[str, Any]
    memory_update: Dict[str, Any]
