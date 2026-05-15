from __future__ import annotations
from pathlib import Path
from .models import CreativeAsset, CreativeIntelligenceReport
from .creative_graph import CreativeGraphBuilder
from .visual_reasoning import VisualReasoningEngine
from .storyboard_memory import StoryboardMemory
from .campaign_memory import CampaignMemory

class CreativeIntelligenceRuntime:
    def run(self, asset: CreativeAsset, output_path: str | Path = "docs/runtime/creative-intelligence-report.json") -> CreativeIntelligenceReport:
        graph = CreativeGraphBuilder().build(asset)
        score, reasoning = VisualReasoningEngine().score(asset)
        storyboard = StoryboardMemory().generate_seed_scenes(asset)
        campaign = CampaignMemory().update(asset, score)
        report = CreativeIntelligenceReport(graph, reasoning, storyboard, campaign, score)
        report.write_json(output_path)
        return report
