from app.lipdub.contracts import LipDubMode, LipDubRequest
from app.lipdub.service import LTXLipDubRuntimeService
from app.runtime.lipdub_contracts import CreativeLipDubWorkflowRequest, CreativeLipDubWorkflowResponse
class CreativeLipDubWorkflow:
    def run(self, req: CreativeLipDubWorkflowRequest):
        lipdub=LTXLipDubRuntimeService().run(LipDubRequest(source_video_path=req.source_video_path, dialogue_text=req.dialogue_text, output_dir=req.output_dir, mode=LipDubMode(req.mode), quality=req.quality, brand_name=req.brand_name, avatar_id=req.avatar_id, campaign_id=req.campaign_id, metadata=req.metadata, save_memory=req.save_memory))
        return CreativeLipDubWorkflowResponse(status='ready_for_postprocess', stage_flow=['Second Brain Recall','LTX LipDub Runtime','Subtitle Karaoke Runtime','Audio Mix Runtime','Final Export','Memory Update'], lipdub=lipdub.model_dump(), next_runtime_handoff={'postprocess_endpoint':'/api/v1/video/postprocess/render','needs':['generated_lipdub_video_path','voice_path_or_audio_track','script','duration'],'recommended_next_module':'kol_subtitle_karaoke_audio_mix_mvp_patch'})
