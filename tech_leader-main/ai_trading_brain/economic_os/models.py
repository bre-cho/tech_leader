from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass(frozen=True)
class EconomicInput:
    revenue: float
    traffic: int
    leads: int
    customers: int
    ad_spend: float
    product_cost: float = 0.0

@dataclass(frozen=True)
class EconomicReport:
    revenue_intelligence: dict
    traffic_intelligence: dict
    funnel_intelligence: dict
    growth_optimization: dict

    def write_json(self, path: str | Path) -> Path:
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return out
