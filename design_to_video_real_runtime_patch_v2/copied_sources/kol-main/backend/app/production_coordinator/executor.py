from __future__ import annotations

from contextlib import closing

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.services.render_orchestrator import RenderOrchestrator
from app.storyboard_engine.schemas import CampaignBrief, PosterInput, ProviderName, StoryboardVariant
from app.storyboard_to_render_bridge import RenderHandoffOptions, StoryboardToRenderBridge

from .schemas import ProductionInput, ProductionPlan, ProductionRunResult, StepRunResult


class GraphProductionCoordinator:
    """Coordinator that turns disconnected modules into one closed-loop flow.

    Phase 1 implementation is deterministic and safe:
    - dry_run / plan_only returns the exact module/API candidates and contract path.
        - execute mode is wired to the canonical poster -> render pipeline and never reports fake final output.
    """

    def run(self, req: ProductionInput, plan: ProductionPlan) -> ProductionRunResult:
        if req.mode in {"dry_run", "plan_only"}:
            return self._dry_run(req, plan)

        # Safe execution skeleton: each step can be wired to actual services later.
        # This prevents fake production success while still enforcing closed-loop contract.
        return self._execute_guarded(req, plan)

    def _dry_run(self, req: ProductionInput, plan: ProductionPlan) -> ProductionRunResult:
        results = []
        for step in plan.steps:
            if not step.enabled:
                results.append(StepRunResult(step_id=step.step_id, status="skipped", message="Disabled by toggle."))
                continue

            if step.status == "blocked":
                results.append(
                    StepRunResult(
                        step_id=step.step_id,
                        status="blocked",
                        message=f"Blocked: no mapped module for required domain {step.domain}.",
                    )
                )
                continue

            results.append(
                StepRunResult(
                    step_id=step.step_id,
                    status="completed",
                    message="Dry-run pass: module candidates resolved and step is connectable.",
                    outputs={
                        "domain": step.domain,
                        "module_candidate_count": len(step.module_candidates),
                        "api_candidate_count": len(step.api_candidates),
                        "output_keys": step.output_keys,
                    },
                )
            )

        status = "blocked" if plan.missing_required_domains else "completed"
        return ProductionRunResult(
            plan_id=plan.plan_id,
            mode=req.mode,
            status=status,
            step_results=results,
            final_contract={
                "dry_run": True,
                "ready_for_execution": not plan.missing_required_domains,
                "missing_required_domains": plan.missing_required_domains,
                "next_action": "Switch mode=execute to run the canonical poster-to-render pipeline.",
            },
        )

    def _build_campaign_brief(self, req: ProductionInput) -> CampaignBrief:
        brief = dict(req.campaign_brief or {})
        if not brief.get("brand"):
            brief["brand"] = "Unknown brand"
        if not brief.get("product"):
            brief["product"] = "Unknown product"
        brief.setdefault("industry", "general")
        brief.setdefault("goal", "conversion")
        brief.setdefault("duration", 30 if int(req.duration_seconds or 30) >= 30 else 15)
        brief.setdefault("platform", req.platform or "tiktok_reels_shorts")
        brief.setdefault("style", "cinematic commercial")
        brief.setdefault("language", "en")
        brief.setdefault("aspect_ratio", req.aspect_ratio or "9:16")
        return CampaignBrief.model_validate(brief)

    def _build_poster_input(self, req: ProductionInput) -> PosterInput:
        valid_providers = [
            ProviderName(provider.lower())
            for provider in req.provider_priority
            if provider.lower() in {provider_name.value for provider_name in ProviderName}
        ]
        if not valid_providers:
            valid_providers = [ProviderName.seedance, ProviderName.kling, ProviderName.runway, ProviderName.veo]
        return PosterInput(
            poster_image_url=req.poster_image_url,
            campaign_brief=self._build_campaign_brief(req),
            requested_variants=[StoryboardVariant.conversion],
            providers=valid_providers,
        )

    @staticmethod
    def _build_handoff_options(req: ProductionInput) -> RenderHandoffOptions:
        supported_providers = {"veo", "runway", "kling", "seedance", "seedance2", "volcengine"}
        providers = [provider.lower() for provider in req.provider_priority if provider.lower() in supported_providers]
        if not providers:
            providers = ["seedance2", "kling", "runway", "veo"]
        return RenderHandoffOptions(
            providers=providers,
            aspect_ratio=req.aspect_ratio or "9:16",
            render_mode="provider_ai_video",
            include_audio=req.enable_audio,
            include_avatar=req.enable_avatar,
            include_drama=req.enable_drama,
            include_voice_clone=False,
            include_smart_subtitle=req.enable_smart_subtitle,
        )

    @staticmethod
    def _open_execute_session():
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            return db
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Production coordinator execute mode requires a live database session. "
                    "Restore DB connectivity or use mode=dry_run."
                ),
            ) from exc

    @staticmethod
    def _collect_degradation_reasons(orchestration_result: dict) -> list[str]:
        reasons: list[str] = []
        for phase_result in (orchestration_result.get("phases") or {}).values():
            if not isinstance(phase_result, dict) or not phase_result.get("degraded"):
                continue
            reason = str(phase_result.get("degradation_reason") or "").strip()
            reasons.append(reason or "A render phase returned degraded output.")
        return reasons

    @staticmethod
    def _resolve_contract_status(*, degraded: bool, orchestration_status: str, final_video_url: str | None) -> str:
        if orchestration_status in {"failed", "partial_failure"}:
            return "failed"
        if degraded or not final_video_url:
            return "degraded"
        return "executed"

    def _execute_guarded(self, req: ProductionInput, plan: ProductionPlan) -> ProductionRunResult:
        results = []
        blocked = bool(plan.missing_required_domains)

        for step in plan.steps:
            if not step.enabled:
                results.append(StepRunResult(step_id=step.step_id, status="skipped", message="Disabled by toggle."))
                continue

            if step.status == "blocked":
                blocked = True
                results.append(
                    StepRunResult(
                        step_id=step.step_id,
                        status="blocked",
                        message=f"Execution blocked: required domain {step.domain} has no module candidate.",
                    )
                )
                continue

            results.append(
                StepRunResult(
                    step_id=step.step_id,
                    status="ready",
                    message=(
                        "Execution will use the canonical poster -> render runtime path for this domain."
                    ),
                    outputs={"candidate_modules": step.module_candidates[:3], "candidate_apis": step.api_candidates[:3]},
                )
            )

        if blocked:
            return ProductionRunResult(
                plan_id=plan.plan_id,
                mode=req.mode,
                status="blocked",
                step_results=results,
                final_contract={
                    "status": "failed",
                    "ready_for_execution": False,
                    "missing_required_domains": plan.missing_required_domains,
                    "message": "Execution blocked because one or more required domains have no mapped module candidate.",
                },
            )

        try:
            bridge = StoryboardToRenderBridge()
            render_package = bridge.build_render_package(
                self._build_poster_input(req),
                self._build_handoff_options(req),
            )
            with closing(self._open_execute_session()) as db_session:
                orchestration_result = RenderOrchestrator().orchestrate(render_package, db_session=db_session)
        except HTTPException as exc:
            return ProductionRunResult(
                plan_id=plan.plan_id,
                mode=req.mode,
                status="failed",
                step_results=results,
                final_contract={
                    "status": "failed",
                    "message": str(exc.detail),
                    "ready_for_execution": False,
                    "no_fake_final_output": True,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ProductionRunResult(
                plan_id=plan.plan_id,
                mode=req.mode,
                status="failed",
                step_results=results,
                final_contract={
                    "status": "failed",
                    "message": str(exc),
                    "ready_for_execution": False,
                    "no_fake_final_output": True,
                },
            )

        phase_3 = orchestration_result.get("phases", {}).get("phase_3", {})
        final_video_url = None
        if isinstance(phase_3, dict):
            final_video_url = phase_3.get("output_url")
        degradation_reasons = self._collect_degradation_reasons(orchestration_result)
        orchestration_status = str(orchestration_result.get("status", "unknown"))
        final_status = self._resolve_contract_status(
            degraded=bool(degradation_reasons),
            orchestration_status=orchestration_status,
            final_video_url=final_video_url,
        )

        if final_status == "executed":
            result_status = "completed"
        elif final_status == "degraded":
            result_status = "completed"
        else:
            result_status = "failed"

        return ProductionRunResult(
            plan_id=plan.plan_id,
            mode=req.mode,
            status=result_status,
            step_results=results,
            final_contract={
                "status": final_status,
                "orchestration_status": orchestration_status,
                "degraded": bool(degradation_reasons),
                "degradation_reasons": degradation_reasons,
                "final_video_url": final_video_url,
                "render_package": render_package,
                "phases": orchestration_result.get("phases", {}),
                "timestamp": orchestration_result.get("timestamp"),
                "no_fake_final_output": True,
                "final_video_contract_exists": bool(final_video_url) and final_status == "executed",
                "message": (
                    "Canonical render pipeline executed successfully."
                    if final_status == "executed"
                    else "Canonical render pipeline completed without a real final video contract."
                ),
            },
        )
