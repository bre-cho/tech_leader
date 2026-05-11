from fastapi import APIRouter
from typing import Any, Dict

router = APIRouter(prefix="/memory", tags=["memory"])

WINNER_DNA_STORE: list[dict[str, Any]] = []


@router.post("/winner-dna")
def save_winner_dna(payload: Dict[str, Any]):
    WINNER_DNA_STORE.append(payload)
    return {"ok": True, "data": {"saved": True, "count": len(WINNER_DNA_STORE)}}


@router.get("/winner-dna/recall")
def recall_winner_dna(industry: str | None = None):
    items = [x for x in WINNER_DNA_STORE if not industry or x.get("industry") == industry]
    return {"ok": True, "data": {"items": items[-10:]}}
