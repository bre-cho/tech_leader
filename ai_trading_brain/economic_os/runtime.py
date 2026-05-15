from __future__ import annotations
from pathlib import Path
from .models import EconomicInput, EconomicReport
from .revenue_intelligence import RevenueIntelligence
from .traffic_intelligence import TrafficIntelligence
from .funnel_intelligence import FunnelIntelligence
from .growth_optimization import GrowthOptimization

class EconomicOSRuntime:
    def run(self, data: EconomicInput, output_path: str | Path = "docs/runtime/economic-os-report.json") -> EconomicReport:
        revenue = RevenueIntelligence().analyze(data)
        traffic = TrafficIntelligence().analyze(data)
        funnel = FunnelIntelligence().analyze(data)
        growth = GrowthOptimization().recommend(revenue, traffic, funnel)
        report = EconomicReport(revenue, traffic, funnel, growth)
        report.write_json(output_path)
        return report
