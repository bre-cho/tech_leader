from __future__ import annotations
from pathlib import Path
from .dependency_evolution_graph import DependencyEvolutionGraph
from .blast_radius_detector import BlastRadiusDetector
from .architecture_drift_detector import ArchitectureDriftDetector
from .models import ArchitectureObserverReport

class ArchitectureObserverRuntime:
    def __init__(self, repo_root: str | Path = "."):
        self.repo_root = Path(repo_root)

    def run(self, changed_files: list[str] | None = None, output_path: str | Path = "docs/runtime/architecture-observer-report.json") -> ArchitectureObserverReport:
        graph = DependencyEvolutionGraph(self.repo_root).build()
        blast = BlastRadiusDetector().detect(changed_files or [], graph)
        drift = ArchitectureDriftDetector().detect(graph)
        report = ArchitectureObserverReport(blast_radius=blast, drift=drift, dependency_evolution=graph)
        report.write_json(self.repo_root / output_path)
        return report
