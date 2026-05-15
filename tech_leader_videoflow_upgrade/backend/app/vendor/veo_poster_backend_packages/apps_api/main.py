import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
import jwt
from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis import Redis, ConnectionPool
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Missing backend dependency: slowapi. Run `pip install -r requirements.txt`."
    ) from exc
from slowapi.util import get_remote_address
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import get_current_user
from apps.api.auth.security import AuthenticatedUser
from apps.api.creative_intelligence import router as creative_intelligence_router
from apps.api.fashion_poster_factory import router as fashion_poster_factory_router
from apps.api.image_upscale import router as image_upscale_router
from apps.api.core.config import settings
from apps.api.db.session import get_db
from apps.api.models.core import BillingUsage, Brand, Project, PosterVariant, Job, ProjectStatus, JobStatus
from apps.api.schemas.core import BillingUsageOut, BrandCreate, BrandOut, DevTokenCreateRequest, DevTokenCreateResponse, ProjectCreate, ProjectOut, VariantOut, JobOut
from packages.scoring_engine.rules import score_prompt
from packages.export_engine.exporter import export_variant_pack
from apps.worker.celery_app import generate_project_job, render_creative_job

logger = logging.getLogger("poster_engine.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(getattr(logging, settings.request_log_level.upper(), logging.INFO))

# Redis connection pool – lazily initialised on first use so that a missing
# or unavailable Redis instance does not crash the process at import time.
# The pool is created once and then reused across all requests.
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


# Rate limiter (P13) – uses the client IP address as the key.
_limiter = Limiter(key_func=get_remote_address)

# Build the rate-limit string once at startup.  When
# RATE_LIMIT_GENERATE_PER_MINUTE is 0 (disabled) we use an extremely high
# ceiling so the decorator is effectively a no-op rather than producing the
# invalid "0/minute" expression.
_GENERATE_RATE_LIMIT: str = (
    f"{settings.rate_limit_generate_per_minute}/minute"
    if settings.rate_limit_generate_per_minute > 0
    else "1000000/minute"
)


def _log_json(payload: dict) -> None:
    logger.info(json.dumps(payload, ensure_ascii=True))


def _run_migrations() -> None:
    project_root = Path(__file__).resolve().parents[2]
    alembic_ini = project_root / "alembic.ini"
    if not alembic_ini.exists():
        _log_json({"event": "migration_skipped", "reason": "alembic_ini_missing"})
        return
    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)

    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            command.upgrade(config, "head")
            _log_json({"event": "migration_applied", "target": "head"})
            return
        except Exception as exc:
            if attempt < max_attempts:
                wait_seconds = 2 ** (attempt - 1)  # 1, 2, 4, 8, 16 s (attempts 1–5)
                _log_json({
                    "event": "migration_retry",
                    "attempt": attempt,
                    "wait_seconds": wait_seconds,
                    "error": str(exc),
                })
                import time as _time
                _time.sleep(wait_seconds)
            else:
                _log_json({"event": "migration_failed", "error": str(exc)})
                raise


def _redis() -> Redis:
    """Return a Redis client that reuses the shared connection pool."""
    return Redis(connection_pool=_get_redis_pool())

@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations()
    yield


app = FastAPI(title="Poster Engine Backend Production MVP", version="0.1.0", lifespan=lifespan)
app.state.limiter = _limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except HTTPException:
        raise
    except Exception:
        _log_json(
            {
                "event": "request_error",
                "request_id": request_id,
                "path": str(request.url.path),
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
        )

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["x-request-id"] = request_id
    _log_json(
        {
            "event": "request",
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
    )
    return response


app.include_router(creative_intelligence_router)
app.include_router(fashion_poster_factory_router)
app.include_router(image_upscale_router)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}


@app.post("/internal/dev/token", response_model=DevTokenCreateResponse)
def create_dev_token(
    payload: DevTokenCreateRequest,
    x_dev_internal_secret: str | None = Header(default=None),
):
    if settings.app_env.lower() in {"prod", "production"}:
        raise HTTPException(status_code=403, detail="Dev token endpoint disabled in production")
    if x_dev_internal_secret != settings.dev_internal_token_secret:
        raise HTTPException(status_code=403, detail="Invalid dev internal secret")

    expires_in_seconds = max(60, min(payload.expires_in_seconds, 86400))
    exp = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
    token_payload = {
        "sub": payload.user_id,
        "email": payload.email,
        "workspace_id": payload.workspace_id,
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(token_payload, settings.auth_jwt_secret, algorithm=settings.auth_jwt_algorithm)
    return DevTokenCreateResponse(access_token=token, expires_in_seconds=expires_in_seconds)

@app.post("/api/v1/brands", response_model=BrandOut)
def create_brand(
    payload: BrandCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = Brand(owner_user_id=user.user_id, **payload.model_dump())
    db.add(brand)
    db.add(
        BillingUsage(
            owner_user_id=user.user_id,
            brand_id=brand.id,
            event_type="brand_created",
            units=1,
            metadata_json={"industry": payload.industry},
        )
    )
    db.commit()
    db.refresh(brand)
    return brand

@app.post("/api/v1/projects", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = db.get(Brand, payload.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this brand")
    project = Project(owner_user_id=user.user_id, **payload.model_dump())
    db.add(project)
    db.add(
        BillingUsage(
            owner_user_id=user.user_id,
            brand_id=brand.id,
            project_id=project.id,
            event_type="project_created",
            units=1,
            metadata_json={"campaign_type": payload.campaign_type},
        )
    )
    db.commit()
    db.refresh(project)
    return project

@app.post("/api/v1/projects/{project_id}/generate")
@_limiter.limit(_GENERATE_RATE_LIMIT)
def generate_project(
    request: Request,
    project_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this project")
    if project.status == ProjectStatus.generating:
        raise HTTPException(
            status_code=409,
            detail="A generation job is already in progress for this project",
        )

    # P10 – Pre-flight billing quota check (monthly window) before enqueuing the Celery job.
    now = datetime.now(UTC)
    used_units: int = (
        db.query(func.coalesce(func.sum(BillingUsage.units), 0))
        .filter(
            BillingUsage.owner_user_id == user.user_id,
            extract("year", BillingUsage.created_at) == now.year,
            extract("month", BillingUsage.created_at) == now.month,
        )
        .scalar()
    ) or 0
    quota = settings.billing_default_quota_per_month
    if used_units >= quota:
        raise HTTPException(
            status_code=402,
            detail=f"Billing quota exceeded: {used_units}/{quota} units used this month",
        )

    redis_client = _redis()
    if idempotency_key:
        redis_key = f"idem:project:{project_id}:{idempotency_key}"
        existing_job_id = redis_client.get(redis_key)
        if existing_job_id:
            existing_job = db.get(Job, existing_job_id)
            if existing_job:
                return {
                    "project_id": project_id,
                    "job_id": existing_job.id,
                    "status": existing_job.status.value,
                    "idempotent_reuse": True,
                }

    project.status = ProjectStatus.generating
    job = Job(
        project_id=project.id,
        job_type="generate_project",
        status=JobStatus.queued,
        provider="internal_celery",
        input_json={"project_id": project_id, "idempotency_key": idempotency_key},
        output_json={"progress": 0, "current_step": "queued"},
    )
    db.add(project)
    db.add(job)
    db.commit()
    db.refresh(job)

    if idempotency_key:
        redis_key = f"idem:project:{project_id}:{idempotency_key}"
        redis_client.setex(redis_key, settings.idempotency_ttl_seconds, job.id)
    redis_client.setex(
        f"job:{job.id}:progress",
        settings.idempotency_ttl_seconds,
        json.dumps({"progress": 0, "current_step": "queued"}),
    )

    generate_project_job.delay(project_id=project_id, job_id=job.id)
    return {
        "project_id": project_id,
        "job_id": job.id,
        "status": job.status.value,
        "idempotent_reuse": False,
    }

@app.get("/api/v1/projects/{project_id}/variants", response_model=list[VariantOut])
def list_variants(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    min_final_score: float | None = Query(default=None, ge=0),
    max_final_score: float | None = Query(default=None, le=100),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this project")

    query = db.query(PosterVariant).filter(PosterVariant.project_id == project_id)
    if status:
        query = query.filter(PosterVariant.status == status)
    if min_final_score is not None:
        query = query.filter(PosterVariant.final_score >= min_final_score)
    if max_final_score is not None:
        query = query.filter(PosterVariant.final_score <= max_final_score)
    return query.order_by(PosterVariant.created_at.desc()).offset(offset).limit(limit).all()

@app.post("/api/v1/variants/{variant_id}/score", response_model=VariantOut)
def score_variant(
    variant_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    variant = db.get(PosterVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    project = db.get(Project, variant.project_id)
    if not project or project.owner_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this variant")
    scores = score_prompt(variant.prompt, variant.variant_type)
    for key, value in scores.items():
        setattr(variant, key, value)
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant

@app.post("/api/v1/variants/{variant_id}/export")
def export_variant(
    variant_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    variant = db.get(PosterVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    project = db.get(Project, variant.project_id)
    if not project or project.owner_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this variant")

    result = export_variant_pack(settings.storage_dir, {
        "id": variant.id,
        "brand_id": project.brand_id,
        "project_id": variant.project_id,
        "source_job_id": None,
        "provider": variant.provider,
        "canva_design_id": variant.canva_design_id,
        "adobe_asset_id": variant.adobe_asset_id,
        # Real provider URLs stored at generation time (P4).
        "image_url": variant.image_url,
        "export_url": variant.export_url,
    })
    variant.status = "exported"
    db.add(variant)
    db.add(
        BillingUsage(
            owner_user_id=user.user_id,
            brand_id=project.brand_id,
            project_id=project.id,
            event_type="variant_exported",
            units=1,
            metadata_json={"variant_id": variant.id},
        )
    )
    db.commit()
    return result

@app.get("/api/v1/jobs/{job_id}", response_model=JobOut)
def get_job(
    job_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.project_id:
        project = db.get(Project, job.project_id)
        if not project or project.owner_user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Forbidden for this job")
    return job


@app.get("/api/v1/jobs/{job_id}/events")
def get_job_events(
    job_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.project_id:
        project = db.get(Project, job.project_id)
        if not project or project.owner_user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Forbidden for this job")

    redis_client = _redis()
    raw_progress = redis_client.get(f"job:{job_id}:progress")
    progress = {"progress": 0, "current_step": "unknown"}
    if raw_progress:
        progress = json.loads(raw_progress)

    variant_count = (
        db.query(PosterVariant)
        .filter(PosterVariant.project_id == job.project_id)
        .with_entities(func.count(PosterVariant.id))
        .scalar()
    )

    return {
        "job_id": job_id,
        "status": job.status.value,
        "current_step": progress.get("current_step"),
        "progress": progress.get("progress", 0),
        "variant_count": variant_count or 0,
        "error_message": job.error_message,
    }


@app.get("/api/v1/billing/usage", response_model=list[BillingUsageOut])
def list_billing_usage(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(BillingUsage)
        .filter(BillingUsage.owner_user_id == user.user_id)
        .order_by(BillingUsage.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@app.get("/api/v1/billing/summary")
def billing_summary(
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    used = (
        db.query(func.coalesce(func.sum(BillingUsage.units), 0))
        .filter(
            BillingUsage.owner_user_id == user.user_id,
            extract("year", BillingUsage.created_at) == now.year,
            extract("month", BillingUsage.created_at) == now.month,
        )
        .scalar()
    )
    quota = settings.billing_default_quota_per_month
    return {
        "user_id": user.user_id,
        "period": "monthly",
        "billing_month": f"{now.year}-{now.month:02d}",
        "used_units": int(used or 0),
        "quota_units": quota,
        "remaining_units": max(quota - int(used or 0), 0),
    }
