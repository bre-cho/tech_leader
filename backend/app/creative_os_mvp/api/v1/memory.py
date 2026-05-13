from fastapi import APIRouter
from app.creative_os_mvp.memory.store import JsonlMemoryStore

router=APIRouter()

@router.get("/winner-dna")
def list_winner_dna(limit: int=50):
    return {"items": JsonlMemoryStore("winner_dna").list(limit)}
