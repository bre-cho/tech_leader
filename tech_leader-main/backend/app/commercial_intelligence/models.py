from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
import hashlib, json, time, uuid

Category = Literal['fmcg','beauty','cosmetics','fashion','wellness','sports_grooming','luxury_branding','ecommerce','billboard','tiktok_ads','performance_marketing']
ExportTarget = Literal['social','tiktok','billboard','print','ecommerce','landing','storyboard']

@dataclass
class CommercialInput:
    brand_name: str
    product_name: str
    category: Category
    audience: str
    business_goal: str
    product_benefits: List[str]
    visual_style: str = 'premium commercial'
    export_targets: List[ExportTarget] = field(default_factory=lambda: ['social'])
    aspect_ratio: str = '4:5'
    headline: Optional[str] = None
    cta: Optional[str] = None
    product_materials: List[str] = field(default_factory=list)
    sensory_effect: Optional[str] = None
    price_tier: Literal['mass','premium','luxury'] = 'premium'
    language: Literal['vi','en','mixed'] = 'vi'

@dataclass
class VisualZone:
    name: str
    role: str
    priority: int
    suggested_position: str
    attention_weight: float
    conversion_role: str

@dataclass
class ReasoningResult:
    attention_route: List[VisualZone]
    typography: Dict[str, Any]
    product_hero: Dict[str, Any]
    environment_reaction: Dict[str, Any]
    psychology: Dict[str, Any]
    billboard_print: Dict[str, Any]
    category_strategy: Dict[str, Any]
    prompt: str
    negative_prompt: str
    scores: Dict[str, float]
    qa: Dict[str, Any]
    artifact_contract: Dict[str, Any]
    storyboard: List[Dict[str, Any]]
    winner_dna: Dict[str, Any]


def stable_id(prefix: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:16]}"


def artifact_contract(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {
        'artifact_id': stable_id(kind, payload),
        'artifact_type': kind,
        'input_hash': payload_hash,
        'created_at': int(time.time()),
        'runtime_version': 'v27.1-v27.7-commercial-intelligence',
        'replayable': True,
        'determinism_mode': 'semantic_deterministic',
        'source': 'commercial_visual_reasoning_engine',
    }
