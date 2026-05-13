from fastapi import APIRouter
from app.schemas.infrastructure import InfrastructureRequest, InfrastructureResponse
from app.runtime.execution_manager import InfrastructureExecutionManager

router = APIRouter(tags=["ai-native-infrastructure"])

@router.post("/infrastructure/run", response_model=InfrastructureResponse)
def run_infrastructure(req: InfrastructureRequest):
    return InfrastructureExecutionManager().run(req.model_dump())

@router.post("/commercial-creative/run")
def run_commercial_creative(req: InfrastructureRequest):
    return InfrastructureExecutionManager().run(req.model_dump())
