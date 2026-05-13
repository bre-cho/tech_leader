from fastapi import APIRouter
from app.creative_infra_mvp.contracts import CreativeRunRequest, CreativeRunResponse
from app.creative_infra_mvp.workflow import CreativeInfrastructureWorkflow
from app.creative_infra_mvp.services.brand_memory_cloud import BrandMemoryCloud

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "system": "AI-Native Creative Business Infrastructure"}

@router.post("/creative-infrastructure/run", response_model=CreativeRunResponse)
def run_creative_infrastructure(payload: CreativeRunRequest):
    return CreativeInfrastructureWorkflow().run(payload)

@router.get("/brand-memory/{brand_name}")
def brand_memory(brand_name: str):
    return {"items": BrandMemoryCloud().recall(brand_name)}
