import json, uuid, hashlib
from time import perf_counter
from sqlalchemy.orm import Session
from app.governance.operating_law import CORE_OPERATING_LAW, OperatingLawEnforcer
from app.runtime.planner import TechnicalLeadPlanner
from app.runtime.router import CapabilityRouter
from app.runtime.verification import VerificationEngine
from app.skills.distiller import SkillDistiller
from app.agents.business_diagnosis import BusinessDiagnosisAgent
from app.agents.image_design import ImageDesignAgent
from app.agents.image_qa import ImageQAAgent
from app.agents.upsell import UpsellOpportunityAgent
from app.agents.video_concept import VideoConceptAgent
from app.agents.storyboard import StoryboardAgent
from app.agents.offer import OfferAgent
from app.context_graph.store import ContextGraphStore
from app.memory.winner_dna import WinnerDNAEngine
from app.models.records import WorkflowRunRecord

class TechnicalLeadOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.law = OperatingLawEnforcer()
        self.planner = TechnicalLeadPlanner()
        self.router = CapabilityRouter()
        self.verifier = VerificationEngine()
        self.distiller = SkillDistiller()
        self.memory = WinnerDNAEngine(db)
        self.graph = ContextGraphStore(db)

    def _run_agent(self, agent, context):
        result = agent.run(context)
        if result["status"] != "succeeded":
            raise RuntimeError(f"{result['agent']} failed: {result.get('error')}")
        return result["output"]

    def run_design_to_video_workflow(self, request):
        workflow_id = str(uuid.uuid4())
        started_at = perf_counter()
        trace = self.law.build_default_trace()
        run = WorkflowRunRecord(
            workflow_id=workflow_id,
            workflow_name="design-to-video",
            status="running",
            input_json=request.model_dump_json(),
        )
        self.db.add(run); self.db.commit(); self.db.refresh(run)

        try:
            # TARGET DEFINE
            target = {"industry": request.industry, "product": request.product, "goal": request.goal, "channel": request.channel}
            trace["target_define"] = True

            # RESEARCH = recall memory + industry heuristic
            recalled = self.memory.recall(request.industry)
            trace["research"] = True

            # PLAN + ROUTE
            plan = self.planner.plan(request.model_dump())
            route = self.router.route(plan)
            trace["plan"] = True

            context = {
                "request": request,
                "workflow_id": workflow_id,
                "target_define": target,
                "recalled_winner_dna": recalled,
                "technical_lead_plan": plan,
                "capability_route": route,
                "trace": trace,
            }

            # EXECUTE SPECIALIZED AGENTS
            context["business_diagnosis"] = self._run_agent(BusinessDiagnosisAgent(), context)
            context["image_concepts"] = self._run_agent(ImageDesignAgent(), context)
            context["image_concepts"] = self._run_agent(ImageQAAgent(), context)
            context["best_concept"] = max(
                context["image_concepts"],
                key=lambda c: c["score"]["conversion_score"] + c["score"]["upsell_video_potential_score"] + c["score"]["trust_score"],
            )
            context["upsell_analysis"] = self._run_agent(UpsellOpportunityAgent(), context)
            context["video_concept"] = self._run_agent(VideoConceptAgent(), context)
            context["storyboard"] = self._run_agent(StoryboardAgent(), context)
            context["offer_packages"] = self._run_agent(OfferAgent(), context)
            trace["execute"] = True

            # DISTILL SKILL
            context["skill_distillation"] = self.distiller.distill(context)
            trace["distill_to_skill"] = True

            # MEMORY PAYLOAD FIRST, VERIFY CAN CHECK MEMORY READY
            best = context["best_concept"]
            dna = {
                "industry": request.industry,
                "visual_type": best["visual_type"],
                "hook": best["headline"],
                "offer": context["offer_packages"][1]["deliverable"],
                "conversion_score": float(best["score"]["conversion_score"]),
                "upsell_rate": 0.0,
                "storyboard_pattern": context["skill_distillation"]["storyboard_pattern"],
                "workflow_id": workflow_id,
            }
            context["winner_dna_payload"] = dna
            artifact = self._build_verification_artifact(context, workflow_id)
            context["artifact"] = artifact

            # MEMORY UPDATE + CONTEXT GRAPH
            if request.dry_run:
                context_graph_update = {
                    "written": False,
                    "skipped": True,
                    "reason": "dry_run_no_persistence",
                }
                memory_update = {
                    "stored": False,
                    "skipped": True,
                    "reason": "dry_run_no_persistence",
                    "dna": dna,
                }
            else:
                self._write_context_graph(request, context, workflow_id)
                context_graph_update = {
                    "written": True,
                    "skipped": False,
                    "reason": None,
                }
                memory_update = self.memory.store(dna)
            trace["memory_update"] = True
            trace["winner_dna_update"] = True

            # VERIFY (after all workflow steps are complete)
            trace["verify"] = True  # Mark verify step before calling verification
            verification = self.verifier.verify(
                context,
                reasoning={"commercial_reasoning_score": float(best["score"]["conversion_score"])},
                artifact=artifact,
            )

            # PROMOTION GATE AFTER LAW TRACE COMPLETE
            if request.dry_run:
                law_decision = self.law.validate_trace(trace)
                checks = verification.get("checks", {}) if verification else {}
                failed_checks = [k for k, v in checks.items() if not v]
                promotion_gate = {
                    "status": "DRY_RUN",
                    "passed": False,
                    "promotable": False,
                    "law_status": law_decision.status,
                    "missing_law_steps": law_decision.missing_steps,
                    "failed_verification_checks": failed_checks,
                    "rule": "DRY_RUN -> NO PROMOTION (preview only)",
                }
            else:
                promotion_gate = self.law.assert_can_promote(trace, verification)

            output = {
                "workflow_id": workflow_id,
                "dry_run": request.dry_run,
                "promotion_mode": "DRY_RUN" if request.dry_run else "REAL",
                "operating_law": CORE_OPERATING_LAW,
                "law_trace": trace,
                "technical_lead_plan": plan,
                "capability_route": route,
                "recalled_winner_dna": recalled,
                "business_diagnosis": context["business_diagnosis"],
                "image_concepts": context["image_concepts"],
                "best_concept": context["best_concept"],
                "upsell_analysis": context["upsell_analysis"],
                "video_concept_preview": context["video_concept"],
                "storyboard": context["storyboard"],
                "offer_packages": context["offer_packages"],
                "skill_distillation": context["skill_distillation"],
                "context_graph_update": context_graph_update,
                "memory_update": memory_update,
                "artifact": artifact,
                "verification": verification,
                "promotion_gate": promotion_gate,
                "observability": {
                    "workflow_seconds": round(perf_counter() - started_at, 4),
                    "verify_passed": verification.get("passed", False),
                    "promotion_status": promotion_gate.get("status"),
                },
            }
            if request.dry_run:
                run.status = "dry_run"
            else:
                run.status = "succeeded" if promotion_gate["passed"] else "blocked"
            run.output_json = json.dumps(output, ensure_ascii=False)
            run.verification_json = json.dumps(verification, ensure_ascii=False)
            run.promotion_status = promotion_gate["status"]
            self.db.commit()
            return output
        except Exception as exc:
            run.status = "failed"
            run.output_json = json.dumps({"error": str(exc), "law_trace": trace}, ensure_ascii=False)
            self.db.commit()
            raise

    def _build_verification_artifact(self, context, workflow_id):
        best = context["best_concept"]
        payload = f"{workflow_id}:{best.get('concept_id','')}:{best.get('prompt','')}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return {
            "artifact_id": f"artifact_{workflow_id[:12]}",
            "checksum": checksum,
            "status": "ready_to_call",
        }

    def _write_context_graph(self, request, context, workflow_id):
        best = context["best_concept"]
        business_key = f"BusinessEntity:{request.industry}:{request.product}"
        audience_key = f"AudienceEntity:{request.audience}"
        creative_key = f"CreativeEntity:{best['concept_id']}"
        poster_key = f"PosterEntity:{best['concept_id']}"
        video_key = f"VideoEntity:{workflow_id}"
        storyboard_key = f"StoryboardEntity:{workflow_id}"
        offer_key = f"OfferEntity:{context['offer_packages'][1]['package']}"
        campaign_key = f"CampaignEntity:{workflow_id}"
        analytics_key = f"AnalyticsEntity:{workflow_id}"
        winner_key = f"WinnerDNAEntity:{workflow_id}"

        self.graph.upsert_entity("BusinessEntity", business_key, context["business_diagnosis"])
        self.graph.upsert_entity("AudienceEntity", audience_key, {"audience": request.audience})
        self.graph.upsert_entity("CreativeEntity", creative_key, best)
        self.graph.upsert_entity("PosterEntity", poster_key, best)
        self.graph.upsert_entity("VideoEntity", video_key, context["video_concept"])
        self.graph.upsert_entity("StoryboardEntity", storyboard_key, {"scenes": context["storyboard"]})
        self.graph.upsert_entity("OfferEntity", offer_key, context["offer_packages"][1])
        self.graph.upsert_entity("CampaignEntity", campaign_key, {"channel": request.channel, "goal": request.goal})
        self.graph.upsert_entity("AnalyticsEntity", analytics_key, {"status": "mvp_placeholder", "tracked_metrics": ["conversion", "upsell_rate", "ctr"]})
        self.graph.upsert_entity("WinnerDNAEntity", winner_key, context["winner_dna_payload"])

        self.graph.add_relation(business_key, "targets", audience_key)
        self.graph.add_relation(business_key, "creates", campaign_key)
        self.graph.add_relation(campaign_key, "uses", creative_key)
        self.graph.add_relation(creative_key, "renders_as", poster_key)
        self.graph.add_relation(poster_key, "upsells_to", video_key)
        self.graph.add_relation(video_key, "planned_by", storyboard_key)
        self.graph.add_relation(video_key, "sold_by", offer_key)
        self.graph.add_relation(campaign_key, "measured_by", analytics_key)
        self.graph.add_relation(analytics_key, "updates", winner_key)
