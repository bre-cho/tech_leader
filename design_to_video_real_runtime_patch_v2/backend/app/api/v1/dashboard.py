from fastapi import APIRouter

from ._utils import standard_response

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/upsell")
def upsell_dashboard():
    return standard_response(
        project_id="dashboard",
        trace_id="dashboard",
        data={
            "image_purchase_rate": 0,
            "video_upsell_rate": 0,
            "best_industries": [],
            "best_offers": [],
            "note": "Wire this endpoint to purchase_events, upsell_opportunities and winner_dna.",
        },
        step="analytics.updated",
    )
