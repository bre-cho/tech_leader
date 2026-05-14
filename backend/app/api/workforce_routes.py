from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.workforce.contracts import WorkforceRunRequest, WorkforceRunResponse
from app.workforce.orchestrator import MultiAgentWorkforceOrchestrator

router = APIRouter(tags=["multi-agent-workforce"])

@router.post("/workforce/image-design/run", response_model=WorkforceRunResponse)
def run_image_design_workforce(payload: WorkforceRunRequest, db: Session = Depends(get_db)):
    return MultiAgentWorkforceOrchestrator(db).run(payload)
