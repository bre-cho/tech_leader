import asyncio
import json
import logging
import time

import httpx
from celery import Celery
from redis import Redis, ConnectionPool

from apps.api.core.config import settings
from apps.api.db.session import SessionLocal
from apps.api.models.core import BillingUsage, Brand, Job, JobStatus, PosterVariant, Project, ProjectStatus
from apps.api.models.creative_intelligence import CreativeRenderJob, CreativeSession
from packages.campaign_intelligence import RenderProviderRegistry
from packages.prompt_engine.beauty import generate_variant_prompts
from packages.provider_adapters.adobe import AdobeMockAdapter, AdobeProductionAdapter
from packages.provider_adapters.base import ProviderError
from packages.provider_adapters.canva import CanvaMockAdapter, CanvaProductionAdapter
from packages.scoring_engine.rules import score_prompt

celery_app = Celery("poster_engine", broker=settings.redis_url, backend=settings.redis_url)

# Schedule the stuck-project cleanup to run every 10 minutes via Celery Beat.
celery_app.conf.beat_schedule = {
    "cleanup-stuck-projects-every-10min": {
        "task": "apps.worker.celery_app.cleanup_stuck_projects",
        "schedule": 600,  # seconds
    },
}

logger = logging.getLogger("poster_engine.worker")

# A1: Redis connection pool is lazily initialised on first use, mirroring the
# pattern in main.py.  This prevents a crash at import time when Redis is not
# yet reachable (e.g. during container startup sequencing or test environments
# that don't start a Redis server).
_redis_pool: ConnectionPool | None = None


def _get_redis_pool() -> ConnectionPool:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=settings.redis_max_connections,
        )
    return _redis_pool


def _redis() -> Redis:
    """Return a Redis client that reuses the lazily-initialised shared pool."""
    return Redis(connection_pool=_get_redis_pool())


def _set_job_progress(job_id: str, progress: int, current_step: str) -> None:
    _redis().setex(
        f"job:{job_id}:progress",
        settings.idempotency_ttl_seconds,
        json.dumps({"progress": progress, "current_step": current_step}),
    )


_TRANSIENT_EXCEPTIONS = (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)


def _run_async(coro):
    """Run an async coroutine safely from synchronous Celery task code.

    A2: Creates a brand-new event loop for each call rather than using
    asyncio.run().  asyncio.run() can raise "This event loop is already
    running" when Celery is configured with a gevent or eventlet pool, because
    those pools install a running loop at the OS-thread level.  Using
    new_event_loop() + run_until_complete() + close() always works regardless
    of the concurrency model.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _retry_call_async(fn, *args, **kwargs):
    """Async version of _retry_call for use with async provider methods."""
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            return await fn(*args, **kwargs)
        except ProviderError as exc:
            last_error = exc
            if not exc.retryable:
                raise
            if attempt < 3:
                await asyncio.sleep(2 ** (attempt - 1))
        except _TRANSIENT_EXCEPTIONS as exc:
            last_error = exc
            if attempt < 3:
                await asyncio.sleep(2 ** (attempt - 1))
    raise last_error  # type: ignore[misc]


def _retry_call(fn, *args, **kwargs):
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            return fn(*args, **kwargs)
        except ProviderError as exc:
            last_error = exc
            if not exc.retryable:
                raise
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))
        except _TRANSIENT_EXCEPTIONS as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))
        # All other exceptions (programming errors, non-transient failures)
        # propagate immediately without retry.
    raise last_error  # type: ignore[misc]


def _build_adobe_adapter():
    if settings.adobe_mode.lower() == "production":
        if not settings.adobe_api_key or not settings.adobe_client_id:
            raise ProviderError(
                "adobe",
                "AUTH",
                retryable=False,
                message="Missing ADOBE_API_KEY or ADOBE_CLIENT_ID",
            )
        return AdobeProductionAdapter(
            access_token=settings.adobe_api_key,
            client_id=settings.adobe_client_id,
            # C3: Use env-specific poll settings so staging adapters don't time out
            # prematurely against a slower staging API.
            poll_max_attempts=settings.effective_adobe_poll_max_attempts,
            poll_interval_seconds=settings.effective_adobe_poll_interval_seconds,
        )
    return AdobeMockAdapter()


def _build_canva_adapter():
    if settings.canva_mode.lower() == "production":
        access_token = settings.canva_access_token
        if not access_token:
            raise ProviderError("canva", "AUTH", retryable=False, message="Missing CANVA_ACCESS_TOKEN")
        return CanvaProductionAdapter(
            access_token=access_token,
            # C3: Use env-specific poll settings.
            poll_max_attempts=settings.effective_canva_poll_max_attempts,
            poll_interval_seconds=settings.effective_canva_poll_interval_seconds,
        )
    return CanvaMockAdapter()

@celery_app.task
def ping():
    return "pong"


@celery_app.task
def render_creative_job(job_id: str, prompt: str, provider: str = "mock") -> dict:
    db = SessionLocal()
    try:
        job = db.get(CreativeRenderJob, job_id)
        if not job:
            return {"error": "job_not_found"}
        job.status = "running"
        db.add(job)
        db.commit()

        context: dict = {}
        if job.session_id:
            session = db.get(CreativeSession, job.session_id)
            if session:
                context.update(
                    {
                        "goal": session.goal,
                        "offer": session.goal,
                        "brand_id": session.brand_id,
                    }
                )
                if session.assets:
                    context["template_id"] = next(
                        (
                            asset.get("template_id")
                            for asset in session.assets
                            if isinstance(asset, dict) and asset.get("template_id")
                        ),
                        None,
                    )
                if session.brand_id:
                    brand = db.get(Brand, session.brand_id)
                    if brand:
                        context["brand"] = brand.name

        result = RenderProviderRegistry().get(provider).generate(prompt, context)
        job.status = "succeeded"
        job.result = result
        job.error = None
        db.add(job)
        db.commit()
        return result
    except Exception as exc:
        job = db.get(CreativeRenderJob, job_id)
        if job:
            job.status = "failed"
            job.error = str(exc)
            db.add(job)
            db.commit()
        raise
    finally:
        db.close()


def _mark_job_failed(job_id: str, error_message: str) -> None:
    """Mark a job (and its associated project) as failed. Safe to call from on_failure."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job:
            job.status = JobStatus.failed
            job.error_message = error_message
            db.add(job)
            if job.project_id:
                project = db.get(Project, job.project_id)
                if project and project.status == ProjectStatus.generating:
                    project.status = ProjectStatus.failed
                    db.add(project)
            db.commit()
        _set_job_progress(job_id, 100, "failed")
    except Exception as exc:
        logger.error("_mark_job_failed: secondary error: %s", exc)
    finally:
        db.close()


@celery_app.task(bind=True)
def generate_project_job(self, project_id: str, job_id: str) -> dict:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        project = db.get(Project, project_id)
        if not job or not project:
            return {"ok": False, "error": "job_or_project_not_found"}
        brand = db.get(Brand, project.brand_id)
        if not brand:
            job.status = JobStatus.failed
            job.error_message = "brand_not_found"
            db.add(job)
            db.commit()
            _set_job_progress(job_id, 100, "failed")
            return {"ok": False, "error": "brand_not_found"}

        job.status = JobStatus.running
        project.status = ProjectStatus.generating
        db.add(job)
        db.add(project)
        db.commit()
        _set_job_progress(job_id, 10, "generating_prompts")

        prompts = generate_variant_prompts(
            project={"product_name": project.product_name, "offer": project.offer},
            brand={"brand_voice": brand.brand_voice},
        )
        if len(prompts) > settings.api_budget_per_project:
            job.status = JobStatus.failed
            job.error_message = "budget_exceeded"
            db.add(job)
            db.commit()
            _set_job_progress(job_id, 100, "failed_budget_exceeded")
            return {"ok": False, "error": "budget_exceeded"}

        adobe = _build_adobe_adapter()
        canva = _build_canva_adapter()
        created_variant_ids: list[str] = []
        provider_audit = []

        total = max(len(prompts), 1)
        for index, item in enumerate(prompts, start=1):
            # Use async polling adapters (via asyncio.run) to avoid blocking
            # the Celery worker thread during provider poll loops.
            try:
                adobe_result = _run_async(
                    _retry_call_async(
                        adobe.generate_visual_async,
                        item["prompt"],
                        {
                            "brand": brand.name,
                            "brand_voice": brand.brand_voice,
                            "colors": brand.colors,
                            "fonts": brand.fonts,
                            "campaign_type": project.campaign_type,
                        },
                    )
                )
            except Exception as adobe_exc:
                # Adobe failed – skip this variant entirely; no Canva call
                # means no API credit is consumed on the other provider.
                logger.warning(
                    "generate_project_job: Adobe failed for variant %s/%s, skipping. Error: %s",
                    index, total, adobe_exc,
                )
                continue

            try:
                canva_result = _run_async(
                    _retry_call_async(
                        canva.create_layout_async,
                        {
                            "prompt": item["prompt"],
                            "brand": brand.name,
                            "brand_id": brand.id,
                            "offer": project.offer,
                            "template_id": project.metadata_json.get("template_id"),
                        },
                    )
                )
            except Exception as canva_exc:
                # Canva failed after Adobe already succeeded. The Adobe credit
                # is spent, so we still create the variant with whatever data
                # is available rather than silently discarding it.
                logger.warning(
                    "generate_project_job: Canva failed for variant %s/%s, "
                    "persisting Adobe-only result. Error: %s",
                    index, total, canva_exc,
                )
                canva_result = {
                    "provider": "canva_error",
                    "canva_design_id": None,
                    "export_url": None,
                    "error": str(canva_exc),
                }
            scores = score_prompt(item["prompt"], item["variant_type"])

            provider_name = f"{adobe_result.get('provider')}+{canva_result.get('provider')}"

            variant = PosterVariant(
                project_id=project.id,
                variant_type=item["variant_type"],
                prompt=item["prompt"],
                provider=provider_name,
                adobe_asset_id=adobe_result.get("adobe_asset_id"),
                canva_design_id=canva_result.get("canva_design_id"),
                # Persist real provider URLs for use at export time (P4).
                image_url=adobe_result.get("image_url"),
                export_url=canva_result.get("export_url"),
                ctr_score=scores["ctr_score"],
                attention_score=scores["attention_score"],
                luxury_score=scores["luxury_score"],
                trust_score=scores["trust_score"],
                product_focus=scores["product_focus"],
                conversion_score=scores["conversion_score"],
                final_score=scores["final_score"],
                status=scores["status"],
            )
            db.add(variant)
            db.flush()
            db.add(
                BillingUsage(
                    owner_user_id=project.owner_user_id,
                    brand_id=brand.id,
                    project_id=project.id,
                    event_type="variant_generated",
                    units=1,
                    metadata_json={"variant_id": variant.id, "provider": provider_name},
                )
            )
            created_variant_ids.append(variant.id)
            provider_audit.append(
                {
                    "variant_type": item["variant_type"],
                    "adobe": adobe_result,
                    "canva": canva_result,
                }
            )

            progress = 10 + int((index / total) * 80)
            _set_job_progress(job_id, progress, f"generated_{index}_of_{total}")

        project.status = ProjectStatus.scored
        job.status = JobStatus.done
        job.output_json = {
            "created_variant_ids": created_variant_ids,
            "provider_audit": provider_audit,
            "variant_count": len(created_variant_ids),
        }
        db.add(project)
        db.add(job)
        db.commit()

        _set_job_progress(job_id, 100, "done")
        return {"ok": True, "created_variant_ids": created_variant_ids}
    except Exception as exc:
        job = db.get(Job, job_id)
        if job:
            job.status = JobStatus.failed
            job.error_message = str(exc)
            db.add(job)
            if job.project_id:
                project = db.get(Project, job.project_id)
                if project and project.status == ProjectStatus.generating:
                    project.status = ProjectStatus.failed
                    db.add(project)
            db.commit()
        _set_job_progress(job_id, 100, "failed")
        return {"ok": False, "error": str(exc)}
    finally:
        db.close()


@celery_app.task
def cleanup_stuck_projects() -> dict:
    """
    Periodic dead-letter recovery task.

    Finds Project rows that have been stuck in 'generating' status for longer
    than STUCK_PROJECT_TIMEOUT_MINUTES (default 30) and resets them to
    'failed', also updating any associated running Job records.  This prevents
    projects from being permanently locked when a worker crashes mid-task.
    """
    from datetime import UTC, datetime, timedelta

    timeout = timedelta(minutes=settings.stuck_project_timeout_minutes)
    cutoff = datetime.now(UTC) - timeout

    db = SessionLocal()
    recovered = []
    try:
        stuck_projects = (
            db.query(Project)
            .filter(
                Project.status == ProjectStatus.generating,
                Project.updated_at <= cutoff,
            )
            .with_for_update(skip_locked=True)
            .all()
        )
        for project in stuck_projects:
            project.status = ProjectStatus.failed
            db.add(project)

            # Also fail any running jobs for this project.
            running_jobs = (
                db.query(Job)
                .filter(
                    Job.project_id == project.id,
                    Job.status == JobStatus.running,
                )
                .all()
            )
            for job in running_jobs:
                job.status = JobStatus.failed
                job.error_message = "Automatically recovered: worker did not complete within timeout"
                db.add(job)
                _set_job_progress(job.id, 100, "failed_timeout_recovery")

            recovered.append(project.id)

        db.commit()
        logger.info("cleanup_stuck_projects: recovered %d stuck projects", len(recovered))
        return {"recovered": recovered, "count": len(recovered)}
    except Exception as exc:
        logger.error("cleanup_stuck_projects failed: %s", exc)
        return {"error": str(exc), "count": 0}
    finally:
        db.close()
