import uuid
from app.creative_infra_mvp.contracts import CreativeRunRequest, CreativeRunResponse, OperatingStage
from app.creative_infra_mvp.operating_law import OperatingLaw
from app.creative_infra_mvp.services.design_system_extractor import DesignSystemExtractor
from app.creative_infra_mvp.services.design_canvas_engine import DesignCanvasEngine
from app.creative_infra_mvp.services.creative_graph_engine import CreativeGraphEngine
from app.creative_infra_mvp.services.brand_memory_cloud import BrandMemoryCloud
from app.creative_infra_mvp.services.prompt_compiler import CreativePromptCompiler
from app.creative_infra_mvp.services.verification import VerificationEngine
from app.creative_infra_mvp.agents.workforce import (
    CreativeDirectorAgent, VisualStrategistAgent, CompositionAgent, TypographyAgent,
    BrandConsistencyAgent, ConversionOptimizationAgent, MotionThinkingAgent,
    IndustryIntelligenceAgent, DesignQAAgent
)

class CreativeInfrastructureWorkflow:
    def __init__(self):
        self.law = OperatingLaw()
        self.extractor = DesignSystemExtractor()
        self.canvas = DesignCanvasEngine()
        self.graph = CreativeGraphEngine()
        self.memory = BrandMemoryCloud()
        self.compiler = CreativePromptCompiler()
        self.verifier = VerificationEngine()

    def run(self, req: CreativeRunRequest):
        run_id = "run_" + uuid.uuid4().hex[:12]
        stages = []

        stages.append(OperatingStage.target_define)
        prior_memory = self.memory.recall(req.business.brand_name)

        stages.append(OperatingStage.research)
        ds = self.extractor.extract(req.business)

        stages.append(OperatingStage.plan)
        regions = self.canvas.plan_regions(req.business, ds)
        edges = self.graph.build(req.business, ds)

        stages.append(OperatingStage.execute)
        agent_outputs = [
            CreativeDirectorAgent().run(req.business),
            VisualStrategistAgent().run(req.business),
            CompositionAgent().run(regions),
            TypographyAgent().run(ds),
            BrandConsistencyAgent().run(ds),
            ConversionOptimizationAgent().run(req.business),
            MotionThinkingAgent().run(req.business),
            IndustryIntelligenceAgent().run(req.business),
            DesignQAAgent().run(),
        ]
        prompt, negative = self.compiler.compile(req.business, ds, regions, edges, agent_outputs)

        stages.append(OperatingStage.verify)
        verification = self.verifier.verify(ds, regions, edges, prompt)
        promotion_status = "PROMOTED_TO_WINNER_DNA_CANDIDATE" if verification.passed else "BLOCKED_BY_VERIFICATION"

        stages.append(OperatingStage.distill_to_skill)
        storyboard = [
            {"scene": 1, "title": "Hook", "logic": "emotional anchor first glance", "duration_sec": 2},
            {"scene": 2, "title": "Product Hero", "logic": "product moves into attention center", "duration_sec": 3},
            {"scene": 3, "title": "Benefit Proof", "logic": "show material/detail/result proof", "duration_sec": 3},
            {"scene": 4, "title": "CTA", "logic": "clear offer and brand end card", "duration_sec": 2},
        ]

        winner_dna = {
            "brand": req.business.brand_name,
            "industry": req.business.industry,
            "colors": ds.colors,
            "typography": ds.typography,
            "visual_language": ds.visual_language,
            "top_graph_edges": [e.model_dump() for e in edges[:5]],
            "verification_score": verification.score,
            "promotion_status": promotion_status,
        }

        stages.append(OperatingStage.memory_update)
        memory_update = {"saved": False}
        if req.save_memory:
            memory_update = self.memory.save({
                "run_id": run_id,
                "brand_name": req.business.brand_name,
                "winner_dna": winner_dna,
                "prompt": prompt,
                "previous_memory_count": len(prior_memory),
            })

        stages.append(OperatingStage.winner_dna_update)
        self.law.validate(stages)

        return CreativeRunResponse(
            run_id=run_id,
            stages_completed=stages,
            operating_law_passed=True,
            design_system=ds,
            canvas_regions=regions,
            creative_graph_edges=edges,
            agent_results=agent_outputs,
            final_prompt=prompt,
            storyboard=storyboard,
            verification=verification,
            promotion_status=promotion_status,
            memory_update=memory_update,
            winner_dna=winner_dna,
        )
