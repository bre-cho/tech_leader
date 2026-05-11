from __future__ import annotations

import os
import copy
import logging
from datetime import datetime, timezone
from typing import Any

from app.models.publish_job import PublishJob
from app.services.publish_providers import (
    HttpPublishProvider,
    MetaPublishProvider,
    SimulatedPublishProvider,
    TikTokPublishProvider,
    YouTubePublishProvider,
)
from app.services.publish_providers.campaign_budget_policy import BudgetExceededError, CampaignBudgetPolicy
from app.services.publish_providers.preflight import PublishPreflightValidator

PUBLISH_MODE_SIMULATED = "SIMULATED"
PUBLISH_MODE_REAL = "REAL"
_logger = logging.getLogger(__name__)
_publish_mode_default_warned = False


def _now() -> datetime:
    # Keep UTC semantics but store naive datetime to match existing repository
    # persistence convention used across SQLAlchemy models.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def resolve_publish_mode() -> str:
    """Resolve effective publish mode from env vars.

    Priority:
    1) PUBLISH_PROVIDER_MODE
    2) PUBLISH_MODE (legacy)

    Values mapped to REAL:
    - REAL
    - youtube / tiktok / meta / reels / instagram / facebook / shorts / http
    """
    raw = (os.getenv("PUBLISH_PROVIDER_MODE") or os.getenv("PUBLISH_MODE") or "").strip().lower()
    if not raw:
        global _publish_mode_default_warned
        if not _publish_mode_default_warned:
            _publish_mode_default_warned = True
            _logger.warning(
                "PUBLISH_PROVIDER_MODE is not set; defaulting publish mode to SIMULATED. "
                "Set PUBLISH_PROVIDER_MODE=REAL (or explicit provider target) for real publishing."
            )
        return PUBLISH_MODE_SIMULATED
    if raw in {"simulated", "simulation"}:
        return PUBLISH_MODE_SIMULATED
    if raw in {"real", "youtube", "tiktok", "meta", "reels", "instagram", "facebook", "shorts", "http"}:
        return PUBLISH_MODE_REAL
    return PUBLISH_MODE_SIMULATED


def resolve_publish_target(platform: str | None = None) -> str:
    """Resolve provider target for real publish execution."""
    mode = (os.getenv("PUBLISH_PROVIDER_MODE") or "").strip().lower()
    if mode and mode not in {"simulated", "real"}:
        return mode
    return str(platform or "youtube").strip().lower()


def is_publish_simulated() -> bool:
    return resolve_publish_mode() == PUBLISH_MODE_SIMULATED


def publish_configuration_snapshot(platform: str | None = None) -> dict[str, Any]:
    return {
        "raw_publish_provider_mode": os.getenv("PUBLISH_PROVIDER_MODE"),
        "raw_publish_mode": os.getenv("PUBLISH_MODE"),
        "resolved_publish_mode": resolve_publish_mode(),
        "resolved_target": resolve_publish_target(platform),
        "simulated": is_publish_simulated(),
    }


class PublishScheduler:
    """Create and execute publish jobs with policy gates."""

    def __init__(
        self,
        *,
        preflight: PublishPreflightValidator | None = None,
        budget_policy: CampaignBudgetPolicy | None = None,
    ) -> None:
        self._preflight = preflight or PublishPreflightValidator()
        self._budget_policy = budget_policy or CampaignBudgetPolicy()

    def create_publish_jobs(
        self,
        db,
        *,
        channel_plan_id: str | None,
        plan_items: list[dict[str, Any]],
        platform: str,
    ) -> list[PublishJob]:
        jobs: list[PublishJob] = []
        publish_mode = resolve_publish_mode()
        platform_key = str(platform or "shorts").strip().lower()

        for item in plan_items:
            payload = copy.deepcopy(item or {})
            metadata = payload.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}
            if payload.get("video_url"):
                metadata.setdefault("video_url", payload.get("video_url"))
            payload["metadata"] = metadata

            job_kwargs = {
                "channel_plan_id": channel_plan_id,
                "platform": platform_key,
                "publish_mode": publish_mode,
                "status": "queued",
                "payload": payload,
                "request_payload": payload,
                "provider_metadata": metadata,
            }
            try:
                job = PublishJob(**job_kwargs)
            except TypeError:
                # Some tests patch PublishJob with a minimal stand-in class that
                # does not accept keyword constructor args.
                job = PublishJob()
                for key, value in job_kwargs.items():
                    setattr(job, key, value)
            db.add(job)
            jobs.append(job)

        db.commit()
        for job in jobs:
            if hasattr(db, "refresh"):
                db.refresh(job)
        return jobs

    def run_job(self, db, job: PublishJob) -> PublishJob:
        try:
            self._budget_policy.check(db, job)
            preflight_errors = self._preflight.validate(job)
            if preflight_errors:
                job.status = "failed"
                job.error_message = "; ".join(preflight_errors)
                job.error_log = {"preflight_errors": preflight_errors}
                db.add(job)
                db.commit()
                if hasattr(db, "refresh"):
                    db.refresh(job)
                return job

            provider = self._resolve_provider(job.platform, job.publish_mode)
            result = provider.execute(job)

            external_ids = {
                "provider_publish_id": result.get("provider_publish_id"),
                "url": result.get("url") or result.get("platform_url"),
                "short_url": result.get("short_url"),
            }
            external_ids = {k: v for k, v in external_ids.items() if v}

            job.provider_response = result
            job.external_ids = external_ids or None
            job.provider_publish_id = str(result.get("provider_publish_id") or "") or None

            if bool(result.get("ok", False)):
                job.status = "published"
                job.published_at = _now()
                job.error_message = None
            else:
                job.status = "failed"
                job.error_message = str(result.get("error") or "publish execution failed")
                job.error_log = {"provider_result": result}

            db.add(job)
            db.commit()
            if hasattr(db, "refresh"):
                db.refresh(job)
            return job
        except BudgetExceededError as exc:
            job.status = "deferred"
            job.error_message = str(exc)
            job.error_log = {"budget_reason": exc.reason, "budget_detail": exc.detail}
            db.add(job)
            db.commit()
            if hasattr(db, "refresh"):
                db.refresh(job)
            return job
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as exc:  # noqa: BLE001
            if hasattr(db, "rollback"):
                db.rollback()
            job.status = "failed"
            job.error_message = str(exc)
            job.error_log = {"exception_type": type(exc).__name__, "error": str(exc)}
            db.add(job)
            db.commit()
            if hasattr(db, "refresh"):
                db.refresh(job)
            return job

    @staticmethod
    def _resolve_provider(platform: str, publish_mode: str):
        if str(publish_mode or "").upper() == PUBLISH_MODE_SIMULATED:
            return SimulatedPublishProvider()

        target = resolve_publish_target(platform)
        if target in {"youtube", "shorts"}:
            return YouTubePublishProvider()
        if target == "tiktok":
            return TikTokPublishProvider()
        if target in {"meta", "reels", "instagram", "facebook"}:
            return MetaPublishProvider()
        return HttpPublishProvider()
