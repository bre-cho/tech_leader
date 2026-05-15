from fastapi import APIRouter
from app.creative_os_mvp.models.schemas import CreativeRequest, CommercialReasoning
from app.creative_os_mvp.commercial.orchestrator import CommercialIntelligenceOrchestrator

router=APIRouter()
engine=CommercialIntelligenceOrchestrator()

@router.post("/reason", response_model=CommercialReasoning)
def reason(req: CreativeRequest):
    return engine.reason(req)
