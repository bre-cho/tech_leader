from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.design import DesignStudioRequest, DesignStudioResponse
from app.runtime.orchestrator import TechnicalLeadOrchestrator
from app.memory.winner_dna import WinnerDNAEngine
from app.context_graph.store import ContextGraphStore
from app.governance.operating_law import CORE_OPERATING_LAW, REQUIRED_CONTEXT_ENTITIES, REQUIRED_LAW_STEPS
from app.agents.storyboard import StoryboardAgent

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "agentic-creative-operating-environment", "strict_law": True}

@router.get("/governance/operating-law")
def operating_law():
    return {"law": CORE_OPERATING_LAW, "required_steps": REQUIRED_LAW_STEPS, "required_context_entities": REQUIRED_CONTEXT_ENTITIES}

@router.post("/design-studio/run", response_model=DesignStudioResponse)
def run_design_studio(payload: DesignStudioRequest, db: Session = Depends(get_db)):
    return TechnicalLeadOrchestrator(db).run_design_to_video_workflow(payload)

@router.post("/storyboard/full")
def run_full_storyboard(payload: DesignStudioRequest, db: Session = Depends(get_db)):
    result = TechnicalLeadOrchestrator(db).run_design_to_video_workflow(payload)
    context = {"request": payload, "video_concept": result["video_concept_preview"]}
    return StoryboardAgent().execute_full(context)

@router.get("/memory/winner-dna")
def list_winner_dna(db: Session = Depends(get_db)):
    return {"items": WinnerDNAEngine(db).list_all()}

@router.get("/context-graph/entities")
def list_context_entities(db: Session = Depends(get_db)):
    return {"items": ContextGraphStore(db).entities()}

@router.get("/context-graph/relations")
def list_context_relations(db: Session = Depends(get_db)):
    return {"items": ContextGraphStore(db).relations()}
