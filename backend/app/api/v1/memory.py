from fastapi import APIRouter
from typing import Any, Dict

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/memory", tags=["memory"])

WINNER_DNA_STORE: list[dict[str, Any]] = []


@router.post("/winner-dna")
def save_winner_dna(payload: Dict[str, Any]):
    project_id, trace_id = require_project_and_trace(payload)
    WINNER_DNA_STORE.append(payload)
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data={"saved": True, "count": len(WINNER_DNA_STORE)},
        step="winner_dna.saved",
    )


@router.get("/winner-dna/recall")
def recall_winner_dna(industry: str | None = None):
    items = [x for x in WINNER_DNA_STORE if not industry or x.get("industry") == industry]
    project_id = "memory-recall"
    trace_id = "memory-recall"
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data={"items": items[-10:]},
        step="winner_dna.recalled",
    )
