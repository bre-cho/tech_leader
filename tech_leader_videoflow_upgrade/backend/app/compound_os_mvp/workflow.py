import json, uuid
from sqlalchemy.orm import Session
from app.compound_os_mvp.schemas import WorkflowRunRequest
from app.compound_os_mvp.db import WorkflowRun
from app.compound_os_mvp.core.operating_law import OperatingLaw
from app.compound_os_mvp.services.brand_memory import BrandMemoryCloud
from app.compound_os_mvp.services.creative_graph import CreativeIntelligenceGraph
from app.compound_os_mvp.services.agents import (
    CreativeDirectorAgent, BrandStrategistAgent, DesignWorkforceAgent, VideoWorkforceAgent,
    ConversionWorkforceAgent, AnalyticsWorkforceAgent, MemoryWorkforceAgent
)
from app.compound_os_mvp.services.campaign_os import CampaignOS
from app.compound_os_mvp.services.optimization import CompoundOptimizationEngine

class CreativeBusinessOSWorkflow:
    def __init__(self):
        self.law = OperatingLaw()
        self.memory = BrandMemoryCloud()
        self.graph = CreativeIntelligenceGraph()
        self.campaigns = CampaignOS()
        self.optimizer = CompoundOptimizationEngine()

    def run(self, db: Session, req: WorkflowRunRequest):
        run_id = "run_" + uuid.uuid4().hex[:12]
        stages = []

        stages.append("WORKSPACE")
        brand = self.memory.get_or_create(db, req.brand_name, req.industry)
        memory = self.memory.recall(brand)

        stages.append("WORKFLOWS")
        campaign = self.campaigns.create_campaign(db, brand, req)

        stages.append("AI_WORKFORCE")
        graph_edges = self.graph.relevant_edges(db, req.industry, req.goal)
        workforce_report = [
            CreativeDirectorAgent().run(req, memory, graph_edges),
            BrandStrategistAgent().run(req, memory),
            DesignWorkforceAgent().run(req, graph_edges),
            VideoWorkforceAgent().run(req),
            ConversionWorkforceAgent().run(req),
            AnalyticsWorkforceAgent().run(),
            MemoryWorkforceAgent().run(memory),
        ]

        stages.append("MEMORY_RECALL")
        stages.append("CREATIVE_GRAPH_REASONING")

        stages.append("VARIANT_GENERATION")
        variants = self.campaigns.generate_variants(db, campaign, req, memory, graph_edges, count=req.variants)

        stages.append("SCORING")
        winner = self.optimizer.select_winner(variants)
        campaign.winning_variant_id = winner.id
        db.commit()

        stages.append("OPTIMIZATION")
        winner_dna = self.optimizer.save_winner_dna(db, brand.id, campaign.id, winner)

        stages.append("MEMORY_UPDATE")
        updated_memory = self.memory.update_from_winner(db, brand, winner_dna)

        stages.append("WINNER_DNA")
        self.law.validate(stages)

        response_variants = []
        for v in variants:
            response_variants.append({
                "id": v.id,
                "name": v.name,
                "layout": v.layout,
                "hook": v.hook,
                "typography": v.typography,
                "visual_style": v.visual_style,
                "offer": v.offer,
                "score": v.score,
                "prompt": v.prompt,
                "storyboard": json.loads(v.storyboard_json or "[]"),
            })

        graph_out = [{
            "source": e.source, "relation": e.relation, "target": e.target,
            "weight": e.weight, "evidence": e.evidence, "observations": e.observations
        } for e in graph_edges]

        report = {
            "winner_variant_id": winner.id,
            "compound_learning": "memory + graph + templates + prediction updated",
            "next_action": "ingest metrics after campaign deployment to reinforce graph edges",
        }

        run = WorkflowRun(
            run_id=run_id,
            campaign_id=campaign.id,
            stages_json=json.dumps(stages),
            status="completed",
            report_json=json.dumps(report, ensure_ascii=False),
        )
        db.add(run)
        db.commit()

        return {
            "run_id": run_id,
            "status": "completed",
            "operating_law_passed": True,
            "campaign_id": campaign.id,
            "brand_memory": updated_memory,
            "creative_graph": graph_out,
            "variants": response_variants,
            "workforce_report": workforce_report,
            "optimization_report": report,
            "winner_dna": winner_dna,
        }
