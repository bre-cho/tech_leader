from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json

@dataclass(frozen=True)
class CreativeAsset:
    asset_id: str
    title: str
    hook: str
    audience: str
    offer: str
    visual_style: str
    platform: str = "youtube"

@dataclass(frozen=True)
class CreativeScore:
    attention: float
    trust: float
    clarity: float
    conversion: float
    viral_potential: float

    @property
    def total(self) -> float:
        return round(self.attention*0.25 + self.trust*0.2 + self.clarity*0.2 + self.conversion*0.25 + self.viral_potential*0.1, 2)

@dataclass(frozen=True)
class StoryboardMemoryItem:
    scene_id: str
    visual_prompt: str
    camera: str
    retention_role: str
    continuity_notes: str

@dataclass(frozen=True)
class CampaignMemoryItem:
    campaign_id: str
    winning_angles: list[str]
    losing_angles: list[str]
    reusable_dna: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class CreativeIntelligenceReport:
    creative_graph: dict[str, Any]
    visual_reasoning: dict[str, Any]
    storyboard_memory: list[StoryboardMemoryItem]
    campaign_memory: CampaignMemoryItem
    score: CreativeScore

    def write_json(self, path: str | Path) -> Path:
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return out
