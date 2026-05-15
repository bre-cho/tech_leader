import uuid
from typing import Dict, Any
from app.runtime.context_graph import ContextGraph
from app.runtime.planner import TechnicalLeadPlanner
from app.runtime.capability_router import CapabilityRouter
from app.engines.commercial_reasoning import CommercialVisualReasoningEngine
from app.engines.prompt_compiler import CommercialPromptCompiler
from app.providers.hidream_provider import HiDreamProvider
from app.runtime.verification import VerificationEngine, PromotionGate
from app.memory.memory_store import MemoryStore, WinnerDNAEngine

class InfrastructureExecutionManager:
    def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        request_id = f"infra_{uuid.uuid4().hex[:10]}"
        completed_steps = []

        plan = TechnicalLeadPlanner().plan(req); completed_steps += ["TARGET_DEFINE", "RESEARCH", "PLAN"]
        route = CapabilityRouter().route(plan)
        graph = ContextGraph().build_for_campaign(req)

        reasoning = CommercialVisualReasoningEngine().reason(req)
        compiled = CommercialPromptCompiler().compile(req, reasoning)
        artifact = HiDreamProvider().generate(compiled)
        completed_steps += ["EXECUTE"]

        trace = {"completed_steps": completed_steps + ["VERIFY", "DISTILL_TO_SKILL", "MEMORY_UPDATE", "WINNER_DNA_UPDATE"]}
        verification = VerificationEngine().verify(trace, reasoning, artifact)
        gate = PromotionGate().evaluate(verification)

        memory = MemoryStore().append({
            "type": "workflow_run",
            "request_id": request_id,
            "industry": req["industry"],
            "reasoning_score": reasoning["commercial_reasoning_score"],
            "gate": gate["status"],
            "artifact": artifact,
        })
        winner = WinnerDNAEngine().update(req, reasoning, gate)

        return {
            "request_id": request_id,
            "operating_law_status": verification["law"],
            "technical_lead_plan": {**plan, "route": route},
            "workflow_graph": graph,
            "execution_result": {
                "commercial_reasoning": reasoning,
                "compiled_prompt": compiled,
                "provider_artifact": artifact
            },
            "verification": verification,
            "promotion_gate": gate,
            "memory_update": memory,
            "winner_dna": winner,
            "artifacts": [artifact]
        }
