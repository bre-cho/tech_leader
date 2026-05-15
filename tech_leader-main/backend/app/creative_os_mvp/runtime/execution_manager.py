import uuid
from app.creative_os_mvp.models.schemas import CreativeRequest, RuntimeStage, CreativeRunResponse
from app.creative_os_mvp.context_graph.graph import CreativeContextGraph
from app.creative_os_mvp.runtime.core_law import CoreOperatingLaw, REQUIRED_PIPELINE
from app.creative_os_mvp.runtime.planner import Planner
from app.creative_os_mvp.runtime.router import CapabilityRouter
from app.creative_os_mvp.commercial.orchestrator import CommercialIntelligenceOrchestrator
from app.creative_os_mvp.hidream.prompt_compiler import HiDreamCommercialPromptCompiler
from app.creative_os_mvp.providers.factory import get_provider
from app.creative_os_mvp.storage.artifacts import ArtifactStore
from app.creative_os_mvp.runtime.verification import VerificationEngine, PromotionGate
from app.creative_os_mvp.memory.store import WinnerDNAEngine
from app.creative_os_mvp.storyboard.expander import StoryboardExpander

class CreativeOSExecutionManager:
    def __init__(self):
        self.law=CoreOperatingLaw(); self.planner=Planner(); self.router=CapabilityRouter()
        self.commercial=CommercialIntelligenceOrchestrator(); self.compiler=HiDreamCommercialPromptCompiler()
        self.store=ArtifactStore(); self.verify_engine=VerificationEngine(); self.gate=PromotionGate(); self.dna=WinnerDNAEngine()
        self.storyboard=StoryboardExpander()

    def run(self, req: CreativeRequest) -> CreativeRunResponse:
        run_id=req.request_id or str(uuid.uuid4())
        stages=[]
        plan=self.planner.plan(req); stages.append(RuntimeStage(name="TARGET_DEFINE", status="passed", details={"goal":plan["goal"]}))
        graph=CreativeContextGraph.from_request(req); stages.append(RuntimeStage(name="RESEARCH", status="passed", details={"context_nodes":len(graph.nodes)}))
        route=self.router.route(plan); stages.append(RuntimeStage(name="PLAN", status="passed", details={"agents":route["agents"]}))
        reasoning=self.commercial.reason(req)
        prompt, negative=self.compiler.compile(req, reasoning)
        provider=get_provider()
        image_bytes=provider.generate(prompt, negative, req)
        artifact=self.store.save(image_bytes, "commercial_visual", "image/png", {"run_id":run_id, "provider": provider.__class__.__name__, "prompt": prompt, "negative_prompt": negative, "reasoning_score": reasoning.total_score})
        stages.append(RuntimeStage(name="EXECUTE", status="passed", details={"artifact_id":artifact.artifact_id}))
        verification=self.verify_engine.verify(reasoning, [artifact], prompt)
        stages.append(RuntimeStage(name="VERIFY", status="passed" if verification["passed"] else "blocked", details=verification))
        skill={"skill_name":"commercial_visual_generation", "category":req.brand.industry, "score":reasoning.total_score}
        stages.append(RuntimeStage(name="DISTILL_TO_SKILL", status="passed", details=skill))
        promotion=self.gate.evaluate(verification, reasoning)
        memory_update={"stored": False}
        if promotion["approved"] and req.save_memory:
            memory_update=self.dna.maybe_store(req, reasoning, promotion, [artifact])
        stages.append(RuntimeStage(name="MEMORY_UPDATE", status="passed" if req.save_memory else "warning", details=memory_update))
        stages.append(RuntimeStage(name="WINNER_DNA_UPDATE", status="passed" if memory_update.get("stored") else "warning", details=memory_update))
        law=self.law.validate([s.name for s in stages])
        if not law.passed:
            stages.append(RuntimeStage(name="CORE_LAW", status="blocked", details={"missing":law.missing}))
            return CreativeRunResponse(run_id=run_id, status="blocked", stages=stages, reasoning=reasoning, prompt=prompt, negative_prompt=negative, artifacts=[artifact], promotion={"approved":False, "reason":law.message})
        return CreativeRunResponse(run_id=run_id, status="completed", stages=stages, reasoning=reasoning, prompt=prompt, negative_prompt=negative, artifacts=[artifact], storyboard=self.storyboard.expand(req, reasoning), memory_update=memory_update, promotion=promotion)
