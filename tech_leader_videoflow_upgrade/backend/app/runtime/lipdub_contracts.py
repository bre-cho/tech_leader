from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.lipdub.contracts import LipDubQuality
class CreativeLipDubWorkflowRequest(BaseModel):
    brand_name: str; avatar_id: str; campaign_id: str; source_video_path: str; dialogue_text: str; output_dir: str
    product_name: Optional[str]=None; mode: str='mock'; quality: LipDubQuality=LipDubQuality.production; save_memory: bool=True; metadata: Dict[str, Any]=Field(default_factory=dict)
class CreativeLipDubWorkflowResponse(BaseModel):
    status: str; stage_flow: list[str]; lipdub: Dict[str, Any]; next_runtime_handoff: Dict[str, Any]
