from typing import Any, Dict
from app.lipdub.contracts import LipDubRequest
class LTXPipelineLipDubAdapter:
    # Boundary for official ltx_pipelines.lipdub in GPU worker.
    def build_payload(self, req: LipDubRequest) -> Dict[str, Any]:
        output=f"{req.output_dir.rstrip('/')}/ltx_lipdub_output.mp4"
        args={'source_video':req.source_video_path,'dialogue':req.dialogue_text,'output':output,'ic_lora_strength':req.ic_lora_strength,'face_region_strength':req.face_region_strength,'seed':req.seed,'quality':req.quality.value}
        if req.speaker_voice_reference_path: args['voice_reference']=req.speaker_voice_reference_path
        return {'engine':'ltx_pipelines.lipdub','command_hint':'python -m ltx_pipelines.lipdub','args':args,'expected_output_path':output,'runtime_notes':['Run inside GPU image with LTX-2.3 checkpoint and IC-LoRA LipDub safetensors mounted.','Keep as worker boundary; API should enqueue jobs in production.']}
