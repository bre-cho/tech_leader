from fastapi import APIRouter
from app.ads_engine.schemas.contracts import AdsGenerateRequest, AdsGenerateResponse, MetricEvent, WinnerScore
from app.ads_engine.services.auto_ads_generator import AutoAdsGenerator
from app.ads_engine.services.video_ads_engine import VideoAdsEngine
from app.ads_engine.services.winner_system import WinnerSystem

router = APIRouter(prefix="/v1/ads-engine", tags=["ads-engine"])

@router.get("/health")
def health():
    return {"status":"ok","modules":["auto_ads_generator","video_ads_engine","ab_test_winner_system","hook_engine_1000_plus"]}

@router.post("/generate", response_model=AdsGenerateResponse)
def generate_ads(payload: AdsGenerateRequest):
    return AutoAdsGenerator().generate(payload)

@router.post("/render-queue")
def build_render_queue(payload: AdsGenerateResponse, provider: str | None = None):
    queue = VideoAdsEngine().build_render_queue([v.model_dump() for v in payload.variants], provider=provider)
    return {"count": len(queue), "queue": queue}

@router.post("/winner-score", response_model=list[WinnerScore])
def winner_score(events: list[MetricEvent]):
    return WinnerSystem().score(events)
