from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/upsell")
def upsell_dashboard():
    return {
        "ok": True,
        "data": {
            "image_purchase_rate": 0,
            "video_upsell_rate": 0,
            "best_industries": [],
            "best_offers": [],
            "note": "Wire this endpoint to purchase_events, upsell_opportunities and winner_dna.",
        },
    }
