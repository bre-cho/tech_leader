import uuid
from pathlib import Path
from app.lipdub.artifacts import write_mock_artifact
from app.lipdub.comfyui_workflow_adapter import LTXLipDubComfyUIWorkflowAdapter
from app.lipdub.contracts import LipDubMode, LipDubRequest, LipDubResponse
from app.lipdub.ltx_pipeline_adapter import LTXPipelineLipDubAdapter
from app.lipdub.qa import LipDubQAEngine
from app.memory.contracts import MemoryCreateRequest, RecallContextRequest
from app.memory.local_second_brain import LocalSecondBrainStore
class LTXLipDubRuntimeService:
    # Creative Execution Graph -> source avatar video/dialogue -> LTX LipDub -> subtitle/audio postprocess.
    def __init__(self): self.memory=LocalSecondBrainStore(); self.qa=LipDubQAEngine()
    def run(self, req: LipDubRequest) -> LipDubResponse:
        run_id='lipdub_'+uuid.uuid4().hex[:12]
        recalled=self.memory.recall_context(RecallContextRequest(brand_name=req.brand_name, avatar_id=req.avatar_id, campaign_id=req.campaign_id, objective='ltx lipdub identity voice delivery context'))
        enriched=req.dialogue_text+'\n\n'+recalled.prompt_context if recalled.memories else req.dialogue_text
        patched=req.model_copy(update={'dialogue_text':enriched})
        if req.mode==LipDubMode.comfyui: payload=LTXLipDubComfyUIWorkflowAdapter().build_payload(patched)
        elif req.mode==LipDubMode.ltx_pipeline: payload=LTXPipelineLipDubAdapter().build_payload(patched)
        else: payload={'engine':'mock_ltx_lipdub','source_video_path':req.source_video_path,'dialogue_text':enriched,'output_dir':req.output_dir,'ic_lora_strength':req.ic_lora_strength,'face_region_strength':req.face_region_strength}
        qa=self.qa.verify_plan(req, payload); Path(req.output_dir).mkdir(parents=True, exist_ok=True)
        artifacts=[]
        if req.mode==LipDubMode.mock:
            artifacts.append(write_mock_artifact(f"{req.output_dir.rstrip('/')}/{run_id}_lipdub_plan.txt", str(payload), 'mock_ltx_lipdub', {'run_id':run_id,'qa_score':qa['score']}))
        mem={'saved':False}
        if req.save_memory:
            rec=self.memory.create(MemoryCreateRequest(kind='lipdub', title=f'LipDub run {run_id}', content=f'Dialogue: {req.dialogue_text}\nMode: {req.mode.value}\nAvatar: {req.avatar_id}\nCampaign: {req.campaign_id}', tags=['ltx','lipdub','video', req.brand_name or 'no_brand'], metadata={'run_id':run_id,'avatar_id':req.avatar_id,'campaign_id':req.campaign_id,'qa':qa}))
            mem={'saved':True,'memory_id':rec.id}
        return LipDubResponse(status='ready_for_worker' if req.mode!=LipDubMode.mock else 'mock_completed', run_id=run_id, mode=req.mode, stage='ltx_lipdub_runtime', recalled_context=recalled.prompt_context, provider_payload=payload, artifacts=artifacts, qa_report=qa, memory_update=mem)
