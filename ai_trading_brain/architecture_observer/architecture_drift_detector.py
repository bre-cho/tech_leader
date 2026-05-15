from __future__ import annotations
from pathlib import Path
from .models import DriftReport, DependencyEvolutionSnapshot

class ArchitectureDriftDetector:
    """Detects simple architecture boundary violations and dependency drift."""

    def __init__(self, forbidden_edges: list[tuple[str, str]] | None = None):
        self.forbidden_edges = forbidden_edges or [
            ("finance", "codenomad_core"),
            ("knowledge_os", "finance_runtime"),
            ("tests", "docs.runtime"),
        ]

    def detect(self, graph: DependencyEvolutionSnapshot) -> DriftReport:
        violations: list[str] = []
        for edge in graph.edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            dotted_src = src.replace("/", ".")
            for left, right in self.forbidden_edges:
                if left in dotted_src and right in tgt:
                    violations.append(f"Forbidden dependency: {src} -> {tgt}")
            if src.startswith("ai_trading_brain/") and "scripts." in tgt:
                violations.append(f"Core module imports script layer: {src} -> {tgt}")
        score = min(100.0, len(violations) * 20.0)
        risk = "low" if score == 0 else "medium" if score < 40 else "high" if score < 80 else "critical"
        recs = ["Giữ dependency một chiều: core → runtime adapter, không để core import script/UI."]
        if violations:
            recs.append("Tách dependency vi phạm sang adapter hoặc interface chung.")
        return DriftReport(score, sorted(set(violations)), risk, recs)
