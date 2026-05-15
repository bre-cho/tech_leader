from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.design import DesignStudioRequest, DesignStudioResponse
from app.schemas.hidream import HiDreamGenerateRequest, HiDreamGenerateResponse
from app.runtime.orchestrator import TechnicalLeadOrchestrator
from app.memory.winner_dna import WinnerDNAEngine
from app.context_graph.store import ContextGraphStore
from app.runtime.trust_graph import TrustGraphStore
from app.runtime.replay import ReplayRuntime
from app.governance.operating_law import CORE_OPERATING_LAW, REQUIRED_CONTEXT_ENTITIES, REQUIRED_LAW_STEPS
from app.agents.storyboard import StoryboardAgent
from app.hidream.service import HiDreamCommercialVisualEngine

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

@router.post("/hidream/commercial-visual/generate", response_model=HiDreamGenerateResponse)
def generate_hidream_commercial_visual(payload: HiDreamGenerateRequest, db: Session = Depends(get_db)):
    return HiDreamCommercialVisualEngine(db).generate(payload)

@router.get("/memory/winner-dna")
def list_winner_dna(db: Session = Depends(get_db)):
    return {"items": WinnerDNAEngine(db).list_all()}

@router.get("/context-graph/entities")
def list_context_entities(db: Session = Depends(get_db)):
    return {"items": ContextGraphStore(db).entities()}

@router.get("/context-graph/relations")
def list_context_relations(db: Session = Depends(get_db)):
    return {"items": ContextGraphStore(db).relations()}

@router.get("/context-graph/neighborhood/{entity_key:path}")
def get_context_neighborhood(entity_key: str, db: Session = Depends(get_db)):
    return ContextGraphStore(db).neighborhood(entity_key)

@router.get("/context-graph/subgraph/{entity_type}")
def get_context_subgraph(entity_type: str, db: Session = Depends(get_db)):
    return ContextGraphStore(db).subgraph(entity_type)

@router.get("/context-graph/path")
def get_context_path(source_key: str, target_key: str, max_depth: int = 4, db: Session = Depends(get_db)):
    return ContextGraphStore(db).path(source_key, target_key, max_depth=max_depth)

@router.get("/trust-graph/agents")
def list_trust_graph_agents(limit: int = 50, db: Session = Depends(get_db)):
    return {"items": TrustGraphStore(db).list_agent_trust(limit=limit)}

@router.get("/trust-graph/agents/{agent_name}")
def get_trust_graph_agent(agent_name: str, db: Session = Depends(get_db)):
    return TrustGraphStore(db).get_agent_trust(agent_name)

@router.post("/runtime/replay/snapshot/{workflow_id}")
def create_replay_snapshot(workflow_id: str, db: Session = Depends(get_db)):
    return ReplayRuntime(db).create_snapshot(workflow_id)

@router.post("/runtime/replay/run/{snapshot_id}")
def run_replay(snapshot_id: str, db: Session = Depends(get_db)):
    return ReplayRuntime(db).replay(snapshot_id)
