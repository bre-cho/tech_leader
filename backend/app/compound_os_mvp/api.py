import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.compound_os_mvp.db import get_db, Brand, Campaign, CreativeVariant, MetricEvent, GraphEdge, init_db
from app.compound_os_mvp.schemas import WorkflowRunRequest, MetricIngest, BrandCreate
from app.compound_os_mvp.workflow import CreativeBusinessOSWorkflow
from app.compound_os_mvp.services.brand_memory import BrandMemoryCloud
from app.compound_os_mvp.services.creative_graph import CreativeIntelligenceGraph
from app.compound_os_mvp.services.optimization import CompoundOptimizationEngine

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "system": "AI-Native Creative Business OS"}

@router.post("/brands")
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    init_db()
    brand = BrandMemoryCloud().get_or_create(db, payload.name, payload.industry, payload.identity)
    return {"id": brand.id, "name": brand.name, "industry": brand.industry, "memory": json.loads(brand.memory_json)}

@router.get("/brands/{brand_name}/memory")
def get_brand_memory(brand_name: str, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.name == brand_name).first()
    if not brand:
        return {"memory": None}
    return {"brand": brand.name, "memory": json.loads(brand.memory_json)}

@router.post("/creative-business-os/run")
def run_os(payload: WorkflowRunRequest, db: Session = Depends(get_db)):
    init_db()
    return CreativeBusinessOSWorkflow().run(db, payload)

@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    rows = db.query(Campaign).order_by(Campaign.id.desc()).limit(50).all()
    return {"items": [
        {
            "id": c.id, "name": c.name, "brand_id": c.brand_id,
            "product_name": c.product_name, "status": c.status,
            "winning_variant_id": c.winning_variant_id
        } for c in rows
    ]}

@router.get("/campaigns/{campaign_id}/variants")
def list_variants(campaign_id: int, db: Session = Depends(get_db)):
    rows = db.query(CreativeVariant).filter(CreativeVariant.campaign_id == campaign_id).all()
    return {"items": [
        {
            "id": v.id, "name": v.name, "layout": v.layout, "hook": v.hook,
            "typography": v.typography, "visual_style": v.visual_style,
            "score": v.score, "prompt": v.prompt,
            "storyboard": json.loads(v.storyboard_json or "[]")
        } for v in rows
    ]}

@router.post("/analytics/ingest")
def ingest_metrics(payload: MetricIngest, db: Session = Depends(get_db)):
    init_db()
    event = MetricEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    result = CompoundOptimizationEngine().ingest_metrics_and_update_scores(db, event)

    variant = db.query(CreativeVariant).filter(CreativeVariant.id == payload.variant_id).first()
    if variant and result["ctr"] > 0.02:
        CreativeIntelligenceGraph().reinforce(
            db,
            source=f"layout:{variant.layout}",
            relation="increases",
            target="ctr",
            delta=0.04,
            evidence=f"Metric ingest event {event.id}: CTR={result['ctr']:.4f}"
        )
        CreativeIntelligenceGraph().reinforce(
            db,
            source=f"hook:{variant.hook}",
            relation="increases",
            target="conversion",
            delta=0.04,
            evidence=f"Metric ingest event {event.id}: CVR={result['cvr']:.4f}"
        )
    return {"event_id": event.id, "learning": result}

@router.get("/creative-graph")
def creative_graph(db: Session = Depends(get_db)):
    init_db()
    CreativeIntelligenceGraph().ensure_seed(db)
    rows = db.query(GraphEdge).order_by(GraphEdge.weight.desc()).limit(100).all()
    return {"items": [
        {
            "source": e.source, "relation": e.relation, "target": e.target,
            "weight": e.weight, "evidence": e.evidence, "observations": e.observations
        } for e in rows
    ]}
