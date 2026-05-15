from __future__ import annotations

import uuid
from app.core.contracts import CreativeOSRequest, CreativeOSResponse, AgentOutput, WorkflowStage
from app.core.operating_law import CoreOperatingLaw
from app.runtime.enterprise_planner import Planner
from app.runtime.enterprise_router import CapabilityRouter
from app.runtime.enterprise_verification import VerificationEngine
from app.runtime.enterprise_promotion_gate import PromotionGate
from app.intelligence.commercial_visual_reasoner import CommercialVisualReasoner
from app.intelligence.prompt_compiler import CommercialPromptCompiler
from app.providers.hidream_provider import HiDreamProvider
from app.storage.artifacts import build_artifact_contract
from app.memory.store import MemoryStore


class CreativeBusinessOSWorkflow:
    def __init__(self):
        self.law = CoreOperatingLaw()
        self.planner = Planner()
        self.router = CapabilityRouter()
        self.reasoner = CommercialVisualReasoner()
        self.compiler = CommercialPromptCompiler()
        self.verifier = VerificationEngine()
        self.gate = PromotionGate()
        self.memory = MemoryStore()

    def run(self, request: CreativeOSRequest) -> CreativeOSResponse:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        completed = []

        completed.append(WorkflowStage.target_define)
        plan = self.planner.plan(request.input)

        completed.append(WorkflowStage.research)
        route = self.router.route(request.input, request.provider)

        completed.append(WorkflowStage.plan)
        decision = self.reasoner.reason(request.input, request.export_targets)

        completed.append(WorkflowStage.execute)
        prompt, negative_prompt = self.compiler.compile(request.input, decision)

        provider = HiDreamProvider(mode=request.provider)
        provider_result = provider.generate(
            prompt,
            negative_prompt,
            metadata={"run_id": run_id, "brand": request.input.brand_name},
        )
        artifact = build_artifact_contract(
            provider_result,
            run_id=run_id,
            workflow_id=request.workflow_id,
            replay_payload=request.model_dump(),
        )

        completed.append(WorkflowStage.verify)
        verification = self.verifier.verify(decision, prompt)
        promotion = self.gate.decide(verification, request.input)

        storyboard = [
            {"scene": 1, "purpose": "Hook", "visual": decision.attention_route[0], "duration_sec": 2},
            {"scene": 2, "purpose": "Product Desire", "visual": "product hero with material detail", "duration_sec": 3},
            {"scene": 3, "purpose": "Trust Proof", "visual": ", ".join(decision.trust_triggers[:2]), "duration_sec": 3},
            {"scene": 4, "purpose": "Conversion", "visual": "benefit + CTA end card", "duration_sec": 2},
        ]

        completed.append(WorkflowStage.distill_to_skill)
        winner_dna = {
            "industry": request.input.industry,
            "product_type": request.input.product_type,
            "attention_route": decision.attention_route,
            "typography": decision.typography_plan,
            "product_hero": decision.product_hero_plan,
            "commercial_psychology": decision.commercial_psychology,
            "score": verification.score,
            "promotion_status": promotion,
        }

        completed.append(WorkflowStage.memory_update)
        memory_update = {"saved": False}
        if request.save_memory:
            memory_update = self.memory.save({
                "run_id": run_id,
                "brand": request.input.brand_name,
                "winner_dna": winner_dna,
                "verification": verification.model_dump(),
            })

        completed.append(WorkflowStage.winner_dna_update)
        self.law.validate_stages(completed)

        return CreativeOSResponse(
            run_id=run_id,
            operating_law_passed=True,
            stages_completed=completed,
            decisions=decision,
            prompt=prompt,
            negative_prompt=negative_prompt,
            agent_outputs=[
                AgentOutput(agent_name="Planner", status="completed", data=plan),
                AgentOutput(agent_name="CapabilityRouter", status="completed", data=route),
                AgentOutput(agent_name="CommercialVisualReasoner", status="completed", data=decision.model_dump()),
                AgentOutput(agent_name="HiDreamProvider", status=provider_result["status"], data=provider_result),
            ],
            verification=verification,
            promotion_status=promotion,
            winner_dna_candidate=winner_dna,
            artifacts=[artifact],
            storyboard=storyboard,
            memory_update=memory_update,
        )
