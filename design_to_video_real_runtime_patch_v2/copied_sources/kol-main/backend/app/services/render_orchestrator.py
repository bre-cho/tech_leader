"""Render Orchestrator — orchestrates Phases 2-6 of render pipeline.

Coordinates:
- Phase 2: Provider dispatch integration
- Phase 3: Audio mix & mux
- Phase 4: Avatar continuity system
- Phase 5: Drama upgrade engine
- Phase 6: Production quality gate
"""
from __future__ import annotations

import logging
import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from app.db.session import SessionLocal
from app.services.render_repository import create_render_job_with_scenes, get_render_job_by_id
from app.workers.render_dispatch_worker import process_render_dispatch

logger = logging.getLogger(__name__)


@dataclass
class Phase2Result:
    """Provider dispatch result."""
    provider: str
    scene_id: int
    payload_id: str
    status: str  # "submitted", "failed", "queued"
    provider_job_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Phase3Result:
    """Audio mix result."""
    render_job_id: str
    narration_job_id: str
    mix_status: str  # "mixed", "pending", "failed"
    audio_output_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Phase4Result:
    """Avatar continuity result."""
    avatar_id: str
    continuity_policy: str
    locked: bool
    scene_mappings: Dict[int, str]  # scene_id -> avatar_profile_id


@dataclass
class Phase5Result:
    """Drama upgrade result."""
    tension_applied: bool
    camera_drama_applied: bool
    continuity_enforced: bool
    upgraded_scenes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Phase6ValidationError:
    """Production gate error."""
    gate: str
    reason: str
    severity: str  # "error", "warning"


@dataclass
class Phase6Result:
    """Quality gate result."""
    passed: bool
    errors: List[Phase6ValidationError] = field(default_factory=list)
    warnings: List[Phase6ValidationError] = field(default_factory=list)
    quality_score: float = 0.0


class RenderOrchestrator:
    """Orchestrates full render pipeline Phases 2-6."""

    def __init__(self):
        # Services are optionally imported and used when needed
        # This keeps the orchestrator lightweight and avoids circular imports
        self.initialized_at = datetime.now().isoformat()

    def orchestrate(
        self,
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """Run full Phase 2-6 orchestration."""
        logger.info("Starting render orchestration")
        
        result = {
            "orchestration_id": str(uuid4()),
            "render_package": render_package,
            "phases": {},
            "status": "success",
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Phase 2: Provider dispatch
            result["phases"]["phase_2"] = self._phase_2_provider_dispatch(render_package, db_session)
            
            # Phase 3: Audio mix & mux
            result["phases"]["phase_3"] = self._phase_3_audio_mix(render_package, db_session)
            
            # Phase 4: Avatar continuity
            result["phases"]["phase_4"] = self._phase_4_avatar_continuity(render_package, db_session)
            
            # Phase 5: Drama upgrade
            result["phases"]["phase_5"] = self._phase_5_drama_upgrade(render_package, db_session)
            
            # Phase 6: Production quality gate
            result["phases"]["phase_6"] = self._phase_6_quality_gate(result, db_session)
            
            # Check if any phase failed
            if not all(p.get("success", False) for p in result["phases"].values()):
                result["status"] = "partial_failure"
                
        except Exception as exc:
            logger.exception("Orchestration failed")
            result["status"] = "failed"
            result["error"] = str(exc)

        return result

    def _phase_2_provider_dispatch(
        self,
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Phase 2: Provider dispatch integration.
        
        Map render_handoff.payloads[] to provider router and queue render tasks.
        """
        logger.info("Phase 2: Provider dispatch integration")
        
        result = {
            "success": True,
            "phase": 2,
            "name": "Provider Dispatch",
            "dispatched_count": 0,
            "queued_count": 0,
            "failed_count": 0,
            "dispatches": [],
            "dispatch_jobs": [],
        }

        try:
            render_handoff = render_package.get("render_handoff", {})
            payloads = render_handoff.get("payloads", [])
            
            if not payloads:
                logger.warning("No payloads to dispatch")
                return result

            # Group payloads by provider -> one render_job per provider for clean FSM tracking.
            payloads_by_provider = {}
            for payload in payloads:
                provider = payload.get("provider", "unknown")
                if provider not in payloads_by_provider:
                    payloads_by_provider[provider] = []
                payloads_by_provider[provider].append(payload)

            # Submit each provider batch through existing dispatch worker.
            for provider, provider_payloads in payloads_by_provider.items():
                logger.info(f"Dispatching {len(provider_payloads)} scenes to {provider}")

                job_result = self._dispatch_provider_batch(
                    provider=provider,
                    provider_payloads=provider_payloads,
                    render_package=render_package,
                    db_session=db_session,
                )

                result["dispatch_jobs"].append(job_result)
                result["dispatches"].extend(job_result.get("scenes", []))
                result["dispatched_count"] += int(job_result.get("submitted", 0))
                result["queued_count"] += int(job_result.get("queued", 0))
                result["failed_count"] += int(job_result.get("failed", 0))

            result["success"] = (result["dispatched_count"] + result["queued_count"]) > 0
            logger.info(
                "Phase 2 complete: %s submitted, %s queued, %s failed",
                result["dispatched_count"],
                result["queued_count"],
                result["failed_count"],
            )
            
        except Exception as exc:
            logger.exception("Phase 2 failed")
            result["success"] = False
            result["error"] = str(exc)

        return result

    def _dispatch_provider_batch(
        self,
        provider: str,
        provider_payloads: List[Dict[str, Any]],
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """Create DB job + scene tasks, then run real dispatch worker for one provider."""
        provider_job = {
            "provider": provider,
            "job_id": None,
            "submitted": 0,
            "queued": 0,
            "failed": 0,
            "status": "queued",
            "scenes": [],
            "error": None,
        }

        # No DB session: support two safe modes
        # 1) default fallback queue mode (no external calls)
        # 2) optional direct provider submit mode when explicitly enabled
        if db_session is None:
            if self._direct_provider_submit_enabled() and self._can_direct_submit_provider(provider):
                return asyncio.run(
                    self._dispatch_provider_batch_direct(
                        provider=provider,
                        provider_payloads=provider_payloads,
                    )
                )
            if self._direct_provider_submit_enabled():
                logger.info(
                    "Direct submit requested but provider %s is not eligible (missing credentials or quota). Falling back to queued mode.",
                    provider,
                )
            return self._dispatch_provider_batch_fallback(provider, provider_payloads)

        try:
            # Build planned scenes compatible with render_repository + dispatch_service.
            planned_scenes = []
            for idx, payload in enumerate(provider_payloads, start=1):
                planned_scenes.append(
                    {
                        "scene_index": int(payload.get("scene_id") or idx),
                        "title": f"scene_{payload.get('scene_id') or idx}_{provider}",
                        "prompt": payload.get("prompt") or "",
                        "negative_prompt": payload.get("negative_prompt"),
                        "aspect_ratio": payload.get("aspect_ratio") or render_package.get("render_handoff", {}).get("aspect_ratio") or "9:16",
                        "duration_seconds": int(payload.get("duration") or 3),
                        "provider_model": payload.get("model"),
                        "metadata": {
                            "source": "phase_2_orchestrator",
                            "scene_id": payload.get("scene_id"),
                            "camera": payload.get("camera"),
                            "motion": payload.get("motion"),
                            "lighting": payload.get("lighting"),
                            "voiceover": payload.get("voiceover"),
                        },
                    }
                )

            # Use shared DB session if provided; else open local session.
            local_session = db_session is None
            db = db_session or SessionLocal()
            try:
                project_id = str(uuid4())
                job = create_render_job_with_scenes(
                    db,
                    project_id=project_id,
                    provider=provider,
                    aspect_ratio=render_package.get("render_handoff", {}).get("aspect_ratio") or "9:16",
                    style_preset=None,
                    subtitle_mode="smart",
                    planned_scenes=planned_scenes,
                )
                provider_job["job_id"] = job.id

                # Real dispatch flow: submit via provider adapter + mark submitted + enqueue poll fallback.
                asyncio.run(process_render_dispatch(db, job.id))

                refreshed = get_render_job_by_id(db, job.id, with_scenes=True)
                if refreshed:
                    provider_job["status"] = refreshed.status
                    provider_job["submitted"] = int(refreshed.completed_scene_count)
                    # submitted scenes are tracked at scene status level, recompute exact counts:
                    submitted = 0
                    queued = 0
                    failed = 0
                    scene_rows: List[Dict[str, Any]] = []
                    for scene in refreshed.scenes or []:
                        if scene.status == "submitted":
                            submitted += 1
                        elif scene.status == "queued":
                            queued += 1
                        elif scene.status in {"failed", "canceled"}:
                            failed += 1
                        scene_rows.append(
                            {
                                "provider": provider,
                                "scene_id": scene.scene_index,
                                "payload_id": scene.id,
                                "status": scene.status,
                                "provider_job_id": scene.provider_task_id or scene.provider_operation_name,
                                "job_id": refreshed.id,
                                "error": scene.error_message,
                            }
                        )
                    provider_job["submitted"] = submitted
                    provider_job["queued"] = queued
                    provider_job["failed"] = failed
                    provider_job["scenes"] = scene_rows
            finally:
                if local_session:
                    db.close()

            return provider_job

        except Exception as exc:
            logger.exception("Failed to dispatch provider batch for %s", provider)
            provider_job["error"] = str(exc)
            provider_job["failed"] = len(provider_payloads)
            provider_job["scenes"] = [
                {
                    "provider": provider,
                    "scene_id": int(p.get("scene_id") or 0),
                    "payload_id": str(uuid4()),
                    "status": "failed",
                    "provider_job_id": None,
                    "job_id": provider_job.get("job_id"),
                    "error": str(exc),
                }
                for p in provider_payloads
            ]
            return provider_job

    @staticmethod
    def _direct_provider_submit_enabled() -> bool:
        return os.getenv("RENDER_ENABLE_DIRECT_PROVIDER_SUBMIT", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    @staticmethod
    def _can_direct_submit_provider(provider: str) -> bool:
        provider_key = (provider or "").strip().lower()

        # Credential presence checks
        if provider_key == "veo":
            if not os.getenv("VEO_API_BASE_URL") or not os.getenv("VEO_API_KEY"):
                return False
        elif provider_key == "runway":
            if not (os.getenv("RUNWAYML_API_SECRET") or os.getenv("RUNWAY_API_KEY")):
                return False
        else:
            # Only enable direct submit for explicitly configured providers.
            return False

        # Quota check (best effort). If DB/quota service is unavailable, prefer safe fallback.
        try:
            from app.services.provider_audit_service import assert_provider_quota_available

            with SessionLocal() as db:
                assert_provider_quota_available(db, provider=provider_key)
        except Exception:
            return False

        return True

    @staticmethod
    def _dispatch_provider_batch_fallback(provider: str, provider_payloads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback for environments without DB/external providers.

        Returns queued records so pipeline can continue without blocking.
        """
        scene_rows = []
        for idx, payload in enumerate(provider_payloads, start=1):
            scene_rows.append(
                {
                    "provider": provider,
                    "scene_id": int(payload.get("scene_id") or idx),
                    "payload_id": str(uuid4()),
                    "status": "queued",
                    "provider_job_id": None,
                    "job_id": None,
                    "error": None,
                }
            )
        return {
            "provider": provider,
            "job_id": None,
            "submitted": 0,
            "queued": len(scene_rows),
            "failed": 0,
            "status": "dry_run_queued",
            "scenes": scene_rows,
            "error": None,
            "degraded": True,
            "mode": "dry_run",
            "degradation_reason": "Provider dispatch used queued fallback because no DB session was provided.",
        }

    async def _dispatch_provider_batch_direct(
        self,
        provider: str,
        provider_payloads: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Direct provider submit path for db_session=None.

        This path is opt-in via RENDER_ENABLE_DIRECT_PROVIDER_SUBMIT=1.
        It attempts real provider API calls with per-scene timeout and records
        accepted/failed states without requiring DB jobs.
        """
        from app.services.provider_router import submit_render_task

        timeout_seconds = float(os.getenv("RENDER_DIRECT_PROVIDER_TIMEOUT_SECONDS", "12"))
        scene_rows: List[Dict[str, Any]] = []
        submitted = 0
        failed = 0

        for idx, payload in enumerate(provider_payloads, start=1):
            scene_id = int(payload.get("scene_id") or idx)
            scene_payload = {
                "prompt_text": payload.get("prompt") or "",
                "provider_model": payload.get("model"),
                "aspect_ratio": payload.get("aspect_ratio") or "9:16",
                "duration_seconds": int(payload.get("duration") or 3),
                "metadata": {
                    "scene_index": scene_id,
                    "source": "render_orchestrator_direct_submit",
                },
            }

            try:
                submit_result = await asyncio.wait_for(
                    submit_render_task(
                        provider=provider,
                        scene_payload=scene_payload,
                        callback_url=None,
                    ),
                    timeout=timeout_seconds,
                )
                if submit_result.accepted:
                    submitted += 1
                    scene_rows.append(
                        {
                            "provider": submit_result.provider or provider,
                            "scene_id": scene_id,
                            "payload_id": str(uuid4()),
                            "status": "submitted",
                            "provider_job_id": submit_result.provider_task_id
                            or submit_result.provider_operation_name,
                            "job_id": None,
                            "error": None,
                        }
                    )
                else:
                    failed += 1
                    scene_rows.append(
                        {
                            "provider": submit_result.provider or provider,
                            "scene_id": scene_id,
                            "payload_id": str(uuid4()),
                            "status": "failed",
                            "provider_job_id": None,
                            "job_id": None,
                            "error": submit_result.error_message or "Provider rejected request",
                        }
                    )
            except asyncio.TimeoutError:
                failed += 1
                scene_rows.append(
                    {
                        "provider": provider,
                        "scene_id": scene_id,
                        "payload_id": str(uuid4()),
                        "status": "failed",
                        "provider_job_id": None,
                        "job_id": None,
                        "error": f"Provider submit timeout after {timeout_seconds}s",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                failed += 1
                scene_rows.append(
                    {
                        "provider": provider,
                        "scene_id": scene_id,
                        "payload_id": str(uuid4()),
                        "status": "failed",
                        "provider_job_id": None,
                        "job_id": None,
                        "error": str(exc),
                    }
                )

        queued = 0
        return {
            "provider": provider,
            "job_id": None,
            "submitted": submitted,
            "queued": queued,
            "failed": failed,
            "status": "submitted" if submitted > 0 else "failed",
            "scenes": scene_rows,
            "error": None,
        }

    def _phase_3_audio_mix(
        self,
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Phase 3: Audio mix & mux.

        When a DB session is available, creates AudioRenderOutput records and
        enqueues Celery tasks (audio.mix_tracks) for each scene that has voiceover
        text.  Without a DB session the plan is logged and returned as ``queued``
        so the orchestrator can still proceed.
        """
        logger.info("Phase 3: Audio mix & mux")

        result: Dict[str, Any] = {
            "success": True,
            "phase": 3,
            "name": "Audio Mix & Mux",
            "audio_plan": render_package.get("audio_plan", {}),
            "tracks_processed": 0,
            "mix_jobs": [],
            "mux_status": "pending",
        }

        try:
            audio_plan = render_package.get("audio_plan", {})

            if not audio_plan.get("enabled", False):
                logger.info("Audio processing disabled — skipping Phase 3")
                result["mux_status"] = "disabled"
                return result

            tracks = audio_plan.get("tracks", [])
            logger.info("Phase 3: processing %d audio tracks", len(tracks))

            if not tracks:
                # Build draft tracks from scene voiceover so downstream TTS can run.
                storyboard = render_package.get("selected_storyboard", {})
                scenes = storyboard.get("scenes", []) if isinstance(storyboard, dict) else []
                synthesized_jobs = []
                for idx, scene in enumerate(scenes, start=1):
                    if not isinstance(scene, dict):
                        continue
                    narration_text = (
                        scene.get("voiceover")
                        or scene.get("narration_text")
                        or scene.get("dialogue")
                        or ""
                    )
                    if not narration_text:
                        continue
                    scene_id = int(scene.get("scene_id") or idx)
                    synthesized_jobs.append(
                        {
                            "scene_id": scene_id,
                            "status": "queued_tts",
                            "narration_text": narration_text,
                        }
                    )
                result["mix_jobs"] = synthesized_jobs
                result["tracks_processed"] = len(synthesized_jobs)
                result["mux_status"] = "queued_tts" if synthesized_jobs else "no_tracks"
                result["degraded"] = True
                result["mode"] = "dry_run"
                result["degradation_reason"] = (
                    "Audio mix generated draft TTS work items because no persisted track records were available."
                )
                return result

            if db_session is None:
                # No DB — record plan intent only; downstream workers will pick up.
                result["tracks_processed"] = len(tracks)
                result["mux_status"] = "queued"
                result["degraded"] = True
                result["mode"] = "dry_run"
                result["degradation_reason"] = (
                    "Audio mix queued intent only because no DB session was provided."
                )
                logger.info(
                    "Phase 3: no DB session — %d tracks queued for async mixing", len(tracks)
                )
                return result

            # DB session available — create AudioRenderOutput rows and enqueue tasks.
            try:
                from app.services.audio.audio_mix_service import (
                    create_audio_render_output,
                    ensure_default_mix_profile,
                )
                from app.workers.audio_mix_worker import mix_audio_tracks_task
            except ImportError as exc:
                logger.warning("Phase 3: audio services unavailable (%s) — queuing intent", exc)
                result["tracks_processed"] = len(tracks)
                result["mux_status"] = "queued"
                return result

            # Resolve a default mix profile once for the whole batch.
            try:
                profile = ensure_default_mix_profile(db_session)
                mix_profile_id = profile.id
            except Exception as exc:
                logger.warning("Phase 3: could not resolve mix profile: %s", exc)
                mix_profile_id = None

            for track in tracks:
                if not isinstance(track, dict):
                    continue
                narration_job_id_raw = track.get("narration_job_id")
                narration_job_id: Optional[str] = str(narration_job_id_raw) if narration_job_id_raw is not None else None
                if not narration_job_id:
                    # No pre-existing narration job — record intent for async TTS.
                    result["mix_jobs"].append(
                        {
                            "scene_id": track.get("scene_id"),
                            "status": "queued_tts",
                            "voiceover": (track.get("voiceover") or "")[:80],
                        }
                    )
                    continue
                try:
                    output_row = create_audio_render_output(
                        db_session,
                        render_job_id=render_package.get("render_job_id"),
                        narration_job_id=narration_job_id,
                        music_asset_id=track.get("music_asset_id"),
                        mix_profile_id=mix_profile_id,
                    )
                    mix_audio_tracks_task.delay(output_row.id)
                    result["mix_jobs"].append(
                        {
                            "scene_id": track.get("scene_id"),
                            "audio_output_id": output_row.id,
                            "status": "enqueued",
                        }
                    )
                    result["tracks_processed"] += 1
                except Exception as exc:
                    logger.warning(
                        "Phase 3: failed to enqueue mix for scene %s: %s",
                        track.get("scene_id"),
                        exc,
                    )
                    result["mix_jobs"].append(
                        {
                            "scene_id": track.get("scene_id"),
                            "status": "enqueue_failed",
                            "error": str(exc),
                        }
                    )

            result["mux_status"] = "enqueued" if result["tracks_processed"] > 0 else "queued"
            logger.info(
                "Phase 3 complete: %d/%d tracks enqueued for mixing",
                result["tracks_processed"],
                len(tracks),
            )

        except Exception as exc:
            logger.exception("Phase 3 failed")
            result["success"] = False
            result["error"] = str(exc)

        return result

    def _phase_4_avatar_continuity(
        self,
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Phase 4: Avatar continuity system.
        
        Lock avatar identity across scenes using avatar_identity_engine.
        """
        logger.info("Phase 4: Avatar continuity")
        
        result = {
            "success": True,
            "phase": 4,
            "name": "Avatar Continuity",
            "avatar_plan": render_package.get("avatar_plan", {}),
            "continuity_locked": False,
            "scene_mappings": {},
        }

        try:
            avatar_plan = render_package.get("avatar_plan", {})
            
            if not avatar_plan.get("enabled", False):
                logger.info("Avatar continuity disabled")
                return result

            continuity_policy = avatar_plan.get("continuity_policy", "lock_identity_across_scenes")
            logger.info(f"Applying continuity policy: {continuity_policy}")

            # Engine hook: continuity analysis is computed per scene transition.
            from app.drama.services.continuity_service import ContinuityService

            storyboard = render_package.get("selected_storyboard", {})
            scenes = storyboard.get("scenes", [])

            continuity_service = ContinuityService()
            previous_state: Dict[str, Any] | None = None
            continuity_reports: List[Dict[str, Any]] = []
            scene_mappings: Dict[int, str] = {}
            for i, scene in enumerate(scenes):
                if not isinstance(scene, dict):
                    continue
                scene_id = int(scene.get("scene_id") or (i + 1))
                scene_context = {
                    "scene_id": scene_id,
                    "scene_index": scene_id,
                    "scene_goal": scene.get("goal") or scene.get("title"),
                }
                current_analysis = {
                    "scene_goal": scene.get("goal") or scene.get("title"),
                    "visible_conflict": scene.get("visible_conflict"),
                    "hidden_conflict": scene.get("hidden_conflict"),
                    "scene_temperature": scene.get("scene_temperature", 0.0),
                    "pressure_level": scene.get("pressure_level", 0.0),
                }
                report = continuity_service.inspect_scene_transition(
                    scene_context=scene_context,
                    current_analysis=current_analysis,
                    previous_scene_state=previous_state,
                    db=db_session,
                )
                continuity_reports.append({"scene_id": scene_id, **report})
                scene_mappings[scene_id] = str(scene.get("avatar_id") or f"avatar_{uuid4().hex[:8]}")
                previous_state = current_analysis
            
            result["continuity_locked"] = len(scene_mappings) > 0
            result["scene_mappings"] = scene_mappings
            result["policy"] = continuity_policy
            result["continuity_reports"] = continuity_reports
            
            logger.info(f"Phase 4 complete: {len(scene_mappings)} scenes locked to avatars")
            
        except Exception as exc:
            logger.exception("Phase 4 failed")
            result["success"] = False
            result["error"] = str(exc)

        return result

    def _phase_5_drama_upgrade(
        self,
        render_package: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Phase 5: Drama upgrade engine.
        
        Apply tension, camera drama, and continuity using drama services.
        """
        logger.info("Phase 5: Drama upgrade")
        
        result = {
            "success": True,
            "phase": 5,
            "name": "Drama Upgrade",
            "drama_plan": render_package.get("drama_plan", {}),
            "tension_applied": False,
            "camera_drama_applied": False,
            "upgraded_scenes": [],
        }

        try:
            drama_plan = render_package.get("drama_plan", {})
            
            if not drama_plan.get("enabled", False):
                logger.info("Drama upgrade disabled")
                return result

            modules = drama_plan.get("modules", [])
            logger.info(f"Applying drama modules: {modules}")

            from app.drama.engines.camera_drama_engine import CameraDramaEngine
            from app.drama.engines.tension_engine import TensionEngine

            tension_engine = TensionEngine()
            camera_engine = CameraDramaEngine()
            storyboard = render_package.get("selected_storyboard", {})
            scenes = storyboard.get("scenes", [])
            
            upgraded_scenes = []
            for scene in scenes:
                if isinstance(scene, dict):
                    upgraded_scene = dict(scene)
                    scene_context = {
                        "scene_id": scene.get("scene_id"),
                        "scene_goal": scene.get("goal") or scene.get("title"),
                        "exposure_risk": float(scene.get("exposure_risk") or 0.3),
                        "time_pressure": float(scene.get("time_pressure") or 0.4),
                        "social_consequence": float(scene.get("social_consequence") or 0.4),
                    }
                    tension = tension_engine.score(intents=[], relationship_snapshots=[], scene_context=scene_context)
                    camera_plan = camera_engine.build_camera_plan(
                        scene_context=scene_context,
                        tension_breakdown=tension,
                        power_shift={
                            "outcome_type": scene.get("outcome_type") or "stable",
                            "dominant_character_id": scene.get("dominant_character_id"),
                        },
                        blocking_plan={"spatial_mode": scene.get("spatial_mode") or "neutral"},
                    )

                    upgraded_scene["tension_level"] = tension.get("tension_score", 0.0)
                    upgraded_scene["camera_drama_plan"] = camera_plan
                    upgraded_scene["camera_drama_applied"] = True
                    upgraded_scenes.append(upgraded_scene)
            
            result["tension_applied"] = "tension_engine" in modules
            result["camera_drama_applied"] = "camera_drama_engine" in modules
            result["upgraded_scenes"] = upgraded_scenes
            
            logger.info(f"Phase 5 complete: {len(upgraded_scenes)} scenes upgraded")
            
        except Exception as exc:
            logger.exception("Phase 5 failed")
            result["success"] = False
            result["error"] = str(exc)

        return result

    def _phase_6_quality_gate(
        self,
        orchestration_result: Dict[str, Any],
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Phase 6: Production quality gate.
        
        Validate render package against hard locks before final assembly.
        """
        logger.info("Phase 6: Production quality gate")
        
        result = {
            "success": True,
            "phase": 6,
            "name": "Quality Gate",
            "checks": {},
            "passed": True,
            "errors": [],
            "warnings": [],
            "quality_score": 0.0,
        }

        try:
            render_package = orchestration_result.get("render_package", {})
            
            # Check hard locks
            quality_checks = self._validate_hard_locks(render_package)
            
            # Check phase results
            phases = orchestration_result.get("phases", {})
            phase_sanity = self._validate_phase_results(phases)
            
            # Check completion rate
            completion_rate = self._calculate_completion_rate(phases)
            
            # Aggregate results
            result["checks"]["hard_locks"] = quality_checks
            result["checks"]["phase_results"] = phase_sanity
            result["checks"]["completion_rate"] = completion_rate
            
            # Determine pass/fail
            errors = [c for c in quality_checks.get("errors", []) if c.get("severity") == "error"]
            warnings = [c for c in quality_checks.get("errors", []) if c.get("severity") == "warning"]
            
            result["errors"] = errors
            result["warnings"] = warnings
            result["passed"] = len(errors) == 0
            result["quality_score"] = (100.0 - len(errors) * 20 - len(warnings) * 5) / 100.0
            
            logger.info(f"Phase 6 complete: passed={result['passed']}, score={result['quality_score']:.2f}")
            
        except Exception as exc:
            logger.exception("Phase 6 failed")
            result["success"] = False
            result["error"] = str(exc)

        return result

    @staticmethod
    def _validate_hard_locks(render_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hard locks before production."""
        hard_rules = render_package.get("hard_rules", [])
        storyboard = render_package.get("selected_storyboard", {})
        render_handoff = render_package.get("render_handoff", {})
        audio_plan = render_package.get("audio_plan", {})
        
        checks = {
            "errors": [],
            "checks_performed": [],
        }

        # Check 1: Poster analysis & storyboard
        if not storyboard:
            checks["errors"].append({
                "gate": "NO_POSTER_ANALYSIS_NO_STORYBOARD",
                "reason": "No storyboard generated",
                "severity": "error",
            })
        else:
            checks["checks_performed"].append("storyboard_validated")

        # Check 2: Scene JSON
        scenes = storyboard.get("scenes", [])
        if not scenes:
            checks["errors"].append({
                "gate": "NO_SCENE_JSON_NO_RENDER",
                "reason": "No scenes in storyboard",
                "severity": "error",
            })
        else:
            checks["checks_performed"].append("scenes_validated")

        # Check 3: Provider payloads
        payloads = render_handoff.get("payloads", [])
        if not payloads:
            checks["errors"].append({
                "gate": "NO_PROVIDER_EXPORT_NO_PRODUCTION",
                "reason": "No provider payloads",
                "severity": "error",
            })
        else:
            checks["checks_performed"].append("payloads_validated")

        # Check 4: Audio plan
        if audio_plan.get("enabled", False) and not audio_plan.get("tracks"):
            checks["errors"].append({
                "gate": "NO_VOICE_NO_SUBTITLE",
                "reason": "Audio enabled but no tracks",
                "severity": "warning",
            })
        else:
            checks["checks_performed"].append("audio_validated")

        return checks

    @staticmethod
    def _validate_phase_results(phases: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual phase results."""
        sanity = {
            "phase_count": len(phases),
            "success_count": sum(1 for p in phases.values() if p.get("success", False)),
            "phases": {}
        }
        
        for phase_name, phase_result in phases.items():
            sanity["phases"][phase_name] = {
                "success": phase_result.get("success", False),
                "name": phase_result.get("name", "unknown"),
            }

        return sanity

    @staticmethod
    def _calculate_completion_rate(phases: Dict[str, Any]) -> float:
        """Calculate overall completion rate."""
        if not phases:
            return 0.0
        
        success_count = sum(1 for p in phases.values() if p.get("success", False))
        return (success_count / len(phases)) * 100.0
