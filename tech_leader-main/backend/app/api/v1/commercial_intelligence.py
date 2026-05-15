from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from dataclasses import asdict
from app.commercial_intelligence.models import CommercialInput
from app.commercial_intelligence.orchestrator import CommercialVisualReasoningOrchestrator

router = APIRouter(prefix='/api/v1/commercial-intelligence', tags=['commercial-intelligence'])

class CommercialRequest(BaseModel):
    brand_name: str
    product_name: str
    category: Literal['fmcg','beauty','cosmetics','fashion','wellness','sports_grooming','luxury_branding','ecommerce','billboard','tiktok_ads','performance_marketing']
    audience: str
    business_goal: str = 'conversion'
    product_benefits: List[str] = Field(default_factory=list)
    visual_style: str = 'premium commercial'
    export_targets: List[Literal['social','tiktok','billboard','print','ecommerce','landing','storyboard']] = Field(default_factory=lambda: ['social'])
    aspect_ratio: str = '4:5'
    headline: Optional[str] = None
    cta: Optional[str] = None
    product_materials: List[str] = Field(default_factory=list)
    sensory_effect: Optional[str] = None
    price_tier: Literal['mass','premium','luxury'] = 'premium'
    language: Literal['vi','en','mixed'] = 'vi'

@router.post('/reason')
def reason(req: CommercialRequest):
    data = CommercialInput(**req.model_dump())
    result = CommercialVisualReasoningOrchestrator().run(data)
    return asdict(result)
