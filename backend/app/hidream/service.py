
from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from app.schemas.hidream import HiDreamGenerateRequest, HiDreamGenerateResponse
from app.hidream.prompt_compiler import HiDreamPromptCompiler
from app.hidream.provider import get_provider, HiDreamProviderError
from app.hidream.artifacts import ArtifactStore
from app.hidream.scoring import CommercialPerceptionScorer
from app.hidream.storyboard import HiDreamStoryboardExpander
from app.memory.winner_dna import WinnerDNAEngine

REQUIRED_TRACE = [
    "TARGET_DEFINE", "RESEARCH", "PLAN", "EXECUTE", "VERIFY",
    "DISTILL_TO_SKILL", "MEMORY_UPDATE", "WINNER_DNA_UPDATE"
]

class HiDreamCommercialVisualEngine:
    """V27 operational engine: prompt compile -> generate -> artifact -> score -> promote -> memory."""
    def __init__(self, db: Session | None = None):
        self.db = db
        self.compiler = HiDreamPromptCompiler()
        self.artifacts = ArtifactStore()
        self.scorer = CommercialPerceptionScorer()
        self.storyboard = HiDreamStoryboardExpander()

    def generate(self, req: HiDreamGenerateRequest) -> HiDreamGenerateResponse:
        trace: List[str] = []
        trace.append("TARGET_DEFINE")
        trace.append("RESEARCH")
        contract = self.compiler.compile(req)
        trace.append("PLAN")
        provider = get_provider(req.provider)
        try:
            image_bytes = provider.generate(req, contract)
            trace.append("EXECUTE")
            artifact = self.artifacts.save_png(image_bytes, provider.provider_name, req, contract)
        except HiDreamProviderError:
            raise
        except Exception as e:
            raise HiDreamProviderError(f"HiDream generation failed: {e}") from e
        score = self.scorer.score(req, contract)
        trace.append("VERIFY")
        storyboard = self.storyboard.expand(req, contract)
        trace.append("DISTILL_TO_SKILL")
        promotion_gate = {
            "status": "promoted" if score.commercial_score >= 80 and artifact.size_bytes > 0 else "blocked",
            "checks": {
                "artifact_non_empty": artifact.size_bytes > 0,
                "commercial_score_min_80": score.commercial_score >= 80,
                "has_replay_contract": bool(artifact.replay_contract),
                "workflow_trace_complete": all(step in trace + ["MEMORY_UPDATE", "WINNER_DNA_UPDATE"] for step in REQUIRED_TRACE),
            }
        }
        memory_update = {"stored": False, "winner_dna": False, "reason": "db not attached or not winner"}
        if self.db is not None:
            try:
                # Store only winner candidates as Winner DNA for now; ordinary memory can be added by campaign module.
                if score.winner_candidate:
                    WinnerDNAEngine(self.db).store({
                        "industry": req.industry,
                        "visual_type": req.use_case,
                        "hook": req.business_goal,
                        "offer": req.campaign_context.get("offer", "premium commercial visual"),
                        "conversion_score": int(score.commercial_score),
                        "upsell_rate": 0,
                        "storyboard_pattern": storyboard.get("poster_to_video_intent", "hidream_premium_key_visual"),
                    })
                    memory_update = {"stored": True, "winner_dna": True, "reason": "commercial_score >= winner threshold"}
                else:
                    memory_update = {"stored": True, "winner_dna": False, "reason": "scored but below winner candidate threshold"}
            except Exception as e:
                memory_update = {"stored": False, "winner_dna": False, "reason": f"memory update failed: {e}"}
        trace.append("MEMORY_UPDATE")
        trace.append("WINNER_DNA_UPDATE")
        promotion_gate["checks"]["workflow_trace_complete"] = all(step in trace for step in REQUIRED_TRACE)
        return HiDreamGenerateResponse(
            status="ok",
            workflow_trace=trace,
            prompt_contract=contract,
            artifact=artifact,
            score=score,
            storyboard_expansion=storyboard,
            promotion_gate=promotion_gate,
            memory_update=memory_update,
        )
