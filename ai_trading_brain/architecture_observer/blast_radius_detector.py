from __future__ import annotations
from .models import BlastRadiusReport, DependencyEvolutionSnapshot

class BlastRadiusDetector:
    """Estimates which files/modules may be affected by a change set."""

    def detect(self, changed_files: list[str], graph: DependencyEvolutionSnapshot) -> BlastRadiusReport:
        changed = set(changed_files)
        direct = set()
        indirect = set()
        for edge in graph.edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            if source in changed or target in changed or any(c.replace('/', '.').removesuffix('.py') in target for c in changed):
                direct.add(source)
        for edge in graph.edges:
            if edge.get("target") in direct:
                indirect.add(edge.get("source", ""))
        direct -= changed
        indirect -= changed | direct
        total = len(direct) + len(indirect)
        risk = "low" if total < 3 else "medium" if total < 8 else "high" if total < 20 else "critical"
        recommendations = [
            "Chạy unit test cho các file bị ảnh hưởng trực tiếp.",
            "Chạy smoke test end-to-end nếu risk từ medium trở lên.",
        ]
        if risk in {"high", "critical"}:
            recommendations.append("Yêu cầu review kiến trúc trước khi merge vì vùng ảnh hưởng lớn.")
        return BlastRadiusReport(sorted(changed), sorted(direct), sorted(indirect), risk, recommendations)
