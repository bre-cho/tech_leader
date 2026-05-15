from fastapi import APIRouter
from app.creative_os_mvp.models.schemas import CreativeRequest, CreativeRunResponse
from app.creative_os_mvp.runtime.execution_manager import CreativeOSExecutionManager

router=APIRouter()
manager=CreativeOSExecutionManager()

@router.post("/run", response_model=CreativeRunResponse)
def run_creative_os(req: CreativeRequest):
    return manager.run(req)
