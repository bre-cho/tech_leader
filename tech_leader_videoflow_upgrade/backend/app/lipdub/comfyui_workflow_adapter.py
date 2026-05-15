from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from app.lipdub.contracts import LipDubRequest
class LTXLipDubComfyUIWorkflowAdapter:
    # Builds ComfyUI payload for LTX-2.3 IC-LoRA LipDub two-stage workflow.
    def __init__(self, workflow_template_path: str|None=None): self.workflow_template_path=workflow_template_path
    def build_payload(self, req: LipDubRequest) -> Dict[str, Any]:
        workflow=self._load_template() if self.workflow_template_path and Path(self.workflow_template_path).exists() else self._minimal_template(req)
        return {'engine':'comfyui_ltx_2_3_ic_lora_lipdub_two_stage_distilled','workflow':workflow,'input_bindings':{'source_video_path':req.source_video_path,'dialogue_text':req.dialogue_text,'speaker_voice_reference_path':req.speaker_voice_reference_path,'seed':req.seed,'ic_lora_strength':req.ic_lora_strength,'face_region_strength':req.face_region_strength,'quality':req.quality.value},'runtime_notes':['Patch actual ComfyUI node IDs from official workflow JSON.','Use LTX-2.3 checkpoint plus IC-LoRA LipDub safetensors.','Two-stage distilled workflow: lip motion pass then refinement/upscale.']}
    def _load_template(self):
        import json; return json.loads(Path(self.workflow_template_path).read_text(encoding='utf-8'))
    def _minimal_template(self, req):
        return {'nodes':{'load_source_video':{'class_type':'VHS_LoadVideo','inputs':{'video':req.source_video_path}},'dialogue_prompt':{'class_type':'Text','inputs':{'text':req.dialogue_text}},'ltx_lipdub_ic_lora':{'class_type':'LTXVideoLipDub','inputs':{'ic_lora_strength':req.ic_lora_strength,'face_region_strength':req.face_region_strength,'preserve_identity':req.preserve_identity,'preserve_background':req.preserve_background,'seed':req.seed}},'save_video':{'class_type':'VHS_SaveVideo','inputs':{'filename_prefix':'ltx_lipdub'}}}}
