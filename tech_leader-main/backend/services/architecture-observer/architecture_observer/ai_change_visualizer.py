from __future__ import annotations
from .models import BlastRadiusReport, CodeGraphSnapshot, DriftReport

def to_mermaid(snapshot: CodeGraphSnapshot, max_edges: int = 120) -> str:
    node_by_id = {n.id: n for n in snapshot.nodes}
    lines = ["graph TD"]
    for node in snapshot.nodes:
        label = f"{node.module}<br/>{node.path}"
        lines.append(f'  {node.id}["{label}"]')
    for edge in snapshot.edges[:max_edges]:
        if edge.source in node_by_id and edge.target in node_by_id:
            lines.append(f"  {edge.source} --> {edge.target}")
    return "\n".join(lines)

def make_change_markdown(after: CodeGraphSnapshot, blast: BlastRadiusReport | None, drift: DriftReport | None) -> str:
    parts = ["# Architecture Change Viewer", "", "## Snapshot Summary", f"- Nodes: {after.summary.get('node_count')}", f"- Edges: {after.summary.get('edge_count')}", f"- Modules: {after.summary.get('module_count')}", ""]
    if blast:
        parts += ["## Blast Radius"] + [f"- {r}" for r in blast.reasons] + [f"- Score: {blast.blast_radius_score}", f"- Risk: {blast.risk_level}", ""]
    if drift:
        parts += ["## Architecture Drift", f"- Passed: {drift.passed}", f"- Drift score: {drift.drift_score}"]
        if drift.violations: parts += ["### Violations"] + [f"- {v}" for v in drift.violations]
        if drift.warnings: parts += ["### Warnings"] + [f"- {w}" for w in drift.warnings]
        parts.append("")
    parts += ["## Mermaid Graph", "```mermaid", to_mermaid(after), "```"]
    return "\n".join(parts)
