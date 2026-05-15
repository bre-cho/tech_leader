from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import get_current_user
from apps.api.auth.security import AuthenticatedUser
from apps.api.db.session import get_db
from apps.api.models.core import Brand
from apps.api.models.creative_intelligence import BrandDNA, CreativePlan, CreativeRenderJob, CreativeSession, PosterScore
from apps.api.schemas.creative_intelligence import (
    BrandDNAOut,
    BrandDNAUpsertRequest,
    CreativePlanOut,
    CreativeSessionCreate,
    CreativeSessionOut,
    RenderJobCreate,
    RenderJobOut,
    ScoreOut,
    ScoreRequest,
)
from apps.worker.celery_app import render_creative_job
from packages.campaign_intelligence import CreativeDirectorBrain, CreativeSkillEngine, DesignSystemRegistry, PosterScoringEngine

router = APIRouter()


def _get_owned_brand(db: Session, brand_id: str, user_id: str) -> Brand:
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this brand")
    return brand


def _get_owned_session(db: Session, session_id: str, user_id: str) -> CreativeSession:
    session = db.get(CreativeSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session_not_found")
    if session.owner_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden for this session")
    return session


@router.post("/api/v1/creative/sessions", response_model=CreativeSessionOut)
def create_session(
    payload: CreativeSessionCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.brand_id:
        _get_owned_brand(db, payload.brand_id, user.user_id)
    session = CreativeSession(owner_user_id=user.user_id, **payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/api/v1/creative/sessions/{session_id}/plan", response_model=CreativePlanOut)
def plan_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, user.user_id)
    session_payload = {
        "industry": session.industry,
        "product": session.product,
        "goal": session.goal,
        "platform": session.platform,
        "audience": session.audience,
        "perception_targets": session.perception_targets or [],
    }
    plan = CreativeDirectorBrain().plan(session_payload)
    db.add(CreativePlan(session_id=session.id, payload=plan))
    db.commit()
    return {"session_id": session.id, **plan}


@router.post("/api/v1/creative/sessions/{session_id}/score", response_model=ScoreOut)
def score_session(
    session_id: str,
    payload: ScoreRequest | None = Body(default=None),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_session(db, session_id, user.user_id)
    plan = payload.creative_plan if payload else None
    if not plan:
        latest = (
            db.query(CreativePlan)
            .filter(CreativePlan.session_id == session_id)
            .order_by(CreativePlan.created_at.desc())
            .first()
        )
        if not latest:
            raise HTTPException(status_code=400, detail="plan_required")
        plan = latest.payload
    score = PosterScoringEngine().score(plan)
    db.add(
        PosterScore(
            session_id=session_id,
            ctr_score=score["ctr_score"],
            luxury_score=score["luxury_score"],
            readability_score=score["readability_score"],
            brand_recall_score=score["brand_recall_score"],
            emotional_score=score["emotional_score"],
            payload=score["analysis"],
        )
    )
    db.commit()
    return score


@router.post("/api/v1/creative/render-jobs", response_model=RenderJobOut)
def create_render_job(
    payload: RenderJobCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.session_id:
        _get_owned_session(db, payload.session_id, user.user_id)
    job = CreativeRenderJob(session_id=payload.session_id, prompt=payload.prompt, provider=payload.provider, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    render_creative_job.delay(job.id, payload.prompt, payload.provider)
    return job


@router.get("/api/v1/creative/render-jobs/{job_id}", response_model=RenderJobOut)
def get_render_job(
    job_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(CreativeRenderJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    if job.session_id:
        _get_owned_session(db, job.session_id, user.user_id)
    return job


@router.get("/api/v1/skills")
def list_skills(user: AuthenticatedUser = Depends(get_current_user)):
    del user
    return {"skills": CreativeSkillEngine().list_skills()}


@router.get("/api/v1/design-systems")
def list_design_systems(user: AuthenticatedUser = Depends(get_current_user)):
    del user
    return {"design_systems": DesignSystemRegistry().list_systems()}


@router.get("/api/v1/creative/brand-dna/{brand_id}", response_model=BrandDNAOut)
def get_brand_dna(
    brand_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = _get_owned_brand(db, brand_id, user.user_id)
    dna = db.get(BrandDNA, brand.id)
    return {"brand_id": brand.id, "dna": dna.dna if dna else None}


@router.put("/api/v1/creative/brand-dna/{brand_id}", response_model=BrandDNAOut)
def upsert_brand_dna(
    brand_id: str,
    payload: BrandDNAUpsertRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = _get_owned_brand(db, brand_id, user.user_id)
    dna = db.get(BrandDNA, brand.id)
    if dna:
        dna.dna = payload.dna
    else:
        dna = BrandDNA(brand_id=brand.id, dna=payload.dna)
        db.add(dna)
    db.commit()
    return {"brand_id": brand.id, "dna": dna.dna}
