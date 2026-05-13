from app.lipdub.contracts import LipDubRequest
class LipDubQAEngine:
    def verify_plan(self, req: LipDubRequest, provider_payload: dict):
        checks={'has_source_video':bool(req.source_video_path),'has_dialogue':len(req.dialogue_text.strip())>=3,'identity_preservation_enabled':req.preserve_identity is True,'background_preservation_enabled':req.preserve_background is True,'ic_lora_strength_safe':0.2<=req.ic_lora_strength<=1.2,'face_region_strength_safe':0.2<=req.face_region_strength<=1.2,'provider_payload_ready':bool(provider_payload)}
        score=round(sum(1 for v in checks.values() if v)/len(checks)*100,2)
        return {'passed':score>=90,'score':score,'checks':checks,'issues':[k for k,v in checks.items() if not v],'lipdub_quality_notes':['Verify lip-sync after generation with visual QA.','Reject identity drift, mouth artifacts, voice mismatch or background distortion.','Pass final output to subtitle/audio postprocess runtime.']}
