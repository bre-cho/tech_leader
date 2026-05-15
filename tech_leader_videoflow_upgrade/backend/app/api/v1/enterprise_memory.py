from fastapi import APIRouter
from app.memory.store import MemoryStore

router = APIRouter(tags=["memory"])

@router.get("/memory/enterprise/winner-dna")
def get_winner_dna(limit: int = 20):
    return {"items": MemoryStore().recent(limit=limit)}
