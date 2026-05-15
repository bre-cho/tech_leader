from fastapi import APIRouter
from app.creative_infra_mvp.contracts import CreativeRunRequest, CreativeRunResponse
from app.creative_infra_mvp.workflow import CreativeInfrastructureWorkflow
from app.creative_infra_mvp.services.brand_memory_cloud import BrandMemoryCloud
from app.creative_infra_mvp.api.infra_patches import router as infra_patch_router
from app.creative_infra_mvp.api.beauty_patches import router as beauty_patch_router

router = APIRouter()
router.include_router(infra_patch_router)
router.include_router(beauty_patch_router)

@router.get("/health")
def health():
    return {"status": "ok", "system": "AI-Native Creative Business Infrastructure"}

@router.post("/creative-infrastructure/run", response_model=CreativeRunResponse)
def run_creative_infrastructure(payload: CreativeRunRequest):
    return CreativeInfrastructureWorkflow().run(payload)

@router.get("/brand-memory/{brand_name}")
def brand_memory(brand_name: str):
    return {"items": BrandMemoryCloud().recall(brand_name)}
