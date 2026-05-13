from fastapi import APIRouter
from app.workforce.contracts import WorkforceRunRequest, WorkforceRunResponse
from app.workforce.orchestrator import MultiAgentWorkforceOrchestrator

router = APIRouter(tags=["multi-agent-workforce"])

@router.post("/workforce/image-design/run", response_model=WorkforceRunResponse)
def run_image_design_workforce(payload: WorkforceRunRequest):
    return MultiAgentWorkforceOrchestrator().run(payload)
