from __future__ import annotations

import hashlib
import uuid
from sqlalchemy.orm import Session
from app.workforce.contracts import (
    WorkforceRunRequest, WorkforceRunResponse, WorkforceContext
)
from app.workforce.agents.creative_director import CreativeDirectorAgent
from app.workforce.agents.visual_strategist import VisualStrategistAgent
from app.workforce.agents.composition import CompositionAgent
from app.workforce.agents.typography import TypographyAgent
from app.workforce.agents.brand_consistency import BrandConsistencyAgent
from app.workforce.agents.conversion import ConversionOptimizationAgent
from app.workforce.agents.motion import MotionThinkingAgent
from app.workforce.agents.industry import IndustryIntelligenceAgent
from app.workforce.agents.design_qa import DesignQAAgent
from app.governance.operating_law import OperatingLawEnforcer
from app.runtime.verification import VerificationEngine
from app.memory.winner_dna import WinnerDNAEngine
from app.context_graph.store import ContextGraphStore
from app.runtime.trust_graph import TrustGraphStore


class MultiAgentWorkforceOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.law = OperatingLawEnforcer()
        self.verifier = VerificationEngine()
        self.memory = WinnerDNAEngine(db)
        self.graph = ContextGraphStore(db)
        self.trust_graph = TrustGraphStore(db)
        # Order matters: upstream agents create context used by downstream agents.
        self.agents = [
            IndustryIntelligenceAgent(),
            CreativeDirectorAgent(),
            VisualStrategistAgent(),
            BrandConsistencyAgent(),
            CompositionAgent(),
            TypographyAgent(),
            ConversionOptimizationAgent(),
            MotionThinkingAgent(),
            DesignQAAgent(),
        ]

    def run(self, request: WorkforceRunRequest) -> WorkforceRunResponse:
        run_id = "workforce_" + uuid.uuid4().hex[:12]
        trace = self.law.build_default_trace()
        trace["target_define"] = True
        trace["research"] = True
        trace["plan"] = True
        context = WorkforceContext(brief=request.brief)
        results = []

        for agent in self.agents:
            result = agent.run(context)
            results.append(result)
            self.trust_graph.update_agent_trust(result.agent_name, float(result.confidence))
        trace["execute"] = True

        final_prompt, negative_prompt = self._compile_prompt(context)
        storyboard = context.decisions.get("motion", {}).get("storyboard", [])
        qa = results[-1].output
        verification_score = qa.get("score", 0)
        artifact = self._build_verification_artifact(run_id, final_prompt)
        trace["distill_to_skill"] = True
        winner_dna = {
            "industry": request.brief.industry,
            "visual_type": "workforce_multi_agent",
            "hook": request.brief.product_name,
            "offer": request.brief.offer or "",
            "brand_name": request.brief.brand_name,
            "attention_route": context.decisions.get("visual_strategy", {}).get("attention_route", []),
            "colors": context.design_system.get("colors", []),
            "typography": context.decisions.get("typography", {}),
            "conversion": context.decisions.get("conversion", {}),
            "storyboard_pattern": storyboard,
            "conversion_score": float(verification_score),
            "upsell_rate": 0.0,
            "workflow_id": run_id,
            "verification_score": verification_score,
        }
        if request.dry_run or not request.save_memory:
            memory_update = {"stored": False, "skipped": True, "reason": "dry_run_or_memory_disabled", "dna": winner_dna}
            context_graph_update = {"written": False, "skipped": True, "reason": "dry_run_or_memory_disabled"}
        else:
            memory_update = self.memory.store(winner_dna)
            self._write_context_graph(run_id, context)
            context_graph_update = {"written": True, "skipped": False, "reason": None}
        trace["memory_update"] = True
        trace["winner_dna_update"] = True
        trace["verify"] = True

        verification = self.verifier.verify(
            {"trace": trace, "artifact": artifact},
            reasoning={"commercial_reasoning_score": float(verification_score)},
            artifact=artifact,
        )
        if request.dry_run:
            law = self.law.validate_trace(trace)
            failed_checks = [k for k, v in verification.get("checks", {}).items() if not v]
            promotion_gate = {
                "status": "DRY_RUN",
                "passed": False,
                "promotable": False,
                "law_status": law.status,
                "missing_law_steps": law.missing_steps,
                "failed_verification_checks": failed_checks,
                "rule": "DRY_RUN -> NO PROMOTION",
            }
        else:
            promotion_gate = self.law.assert_can_promote(trace, verification)

        promotion_status = "PROMOTED_TO_WORKFLOW_RUNTIME" if promotion_gate.get("passed") else "BLOCKED_BY_GOVERNANCE"

        return WorkforceRunResponse(
            run_id=run_id,
            status="completed",
            dry_run=request.dry_run,
            law_trace=trace,
            context=context,
            agent_results=results,
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            storyboard=storyboard,
            artifact=artifact,
            verification=verification,
            verification_score=verification_score,
            promotion_status=promotion_status,
            promotion_gate=promotion_gate,
            memory_update=memory_update,
            context_graph_update=context_graph_update,
            winner_dna=winner_dna,
        )

    def _compile_prompt(self, context: WorkforceContext):
        b = context.brief
        d = context.decisions
        prompt = f'''
AI COMMERCIAL DESIGN WORKFORCE OUTPUT

Brand: {b.brand_name}
Industry: {b.industry}
Product: {b.product_name} ({b.product_type})
Audience: {b.target_audience}
Goal: {b.campaign_goal}
Channel: {b.channel}

Creative Direction:
{d.get("creative_direction", {})}

Visual Strategy:
{d.get("visual_strategy", {})}

Brand System:
{context.design_system}

Composition Canvas:
{context.canvas_regions}

Typography:
{d.get("typography", {})}

Conversion Logic:
{d.get("conversion", {})}

Motion / Poster-to-Video Logic:
{d.get("motion", {})}

Render a premium, commercial, conversion-focused creative asset.
It must route attention intentionally, preserve brand consistency, keep product readable,
use typography-safe regions, and prepare for poster-to-video expansion.
'''
        negative = "generic AI output, distorted logo, unreadable text, broken anatomy, fake product, clutter, low contrast, off-brand colors"
        return prompt.strip(), negative

    def _build_verification_artifact(self, run_id: str, final_prompt: str):
        checksum = hashlib.sha256(final_prompt.encode("utf-8")).hexdigest()
        return {
            "artifact_id": f"artifact_{run_id}",
            "checksum": checksum,
            "status": "ready_to_call",
        }

    def _write_context_graph(self, run_id: str, context: WorkforceContext):
        brief = context.brief
        business_key = f"BusinessEntity:{brief.industry}:{brief.brand_name}"
        audience_key = f"AudienceEntity:{brief.target_audience}"
        creative_key = f"CreativeEntity:{run_id}"
        campaign_key = f"CampaignEntity:{run_id}"
        winner_key = f"WinnerDNAEntity:{run_id}"
        self.graph.upsert_entity("BusinessEntity", business_key, brief.model_dump())
        self.graph.upsert_entity("AudienceEntity", audience_key, {"audience": brief.target_audience})
        self.graph.upsert_entity("CreativeEntity", creative_key, context.decisions)
        self.graph.upsert_entity("CampaignEntity", campaign_key, {"channel": brief.channel, "goal": brief.campaign_goal})
        self.graph.upsert_entity("WinnerDNAEntity", winner_key, context.qa_checks)
        self.graph.add_relation(business_key, "targets", audience_key)
        self.graph.add_relation(business_key, "creates", campaign_key)
        self.graph.add_relation(campaign_key, "uses", creative_key)
        self.graph.add_relation(campaign_key, "updates", winner_key)
