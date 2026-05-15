from __future__ import annotations
from .dependency_mapper import affected_by
from .models import BlastRadiusReport, CodeGraphSnapshot

def analyze_blast_radius(before: CodeGraphSnapshot, after: CodeGraphSnapshot) -> BlastRadiusReport:
    before_paths, after_paths = {n.path: n for n in before.nodes}, {n.path: n for n in after.nodes}
    changed_files = []
    for path, node in after_paths.items():
        old = before_paths.get(path)
        if old is None or old.size_bytes != node.size_bytes or old.lines != node.lines or old.imports != node.imports or old.risk_tags != node.risk_tags:
            changed_files.append(path)
    for path in before_paths:
        if path not in after_paths:
            changed_files.append(path)
    after_id_by_path = {n.path: n.id for n in after.nodes}
    changed_ids = [after_id_by_path[p] for p in changed_files if p in after_id_by_path]
    impacted = affected_by(after, changed_ids, depth=2)
    node_by_id = {n.id: n for n in after.nodes}
    touched_modules = sorted(set(node_by_id[i].module for i in impacted if i in node_by_id))
    impacted_edges = [e for e in after.edges if e.source in impacted or e.target in impacted]
    score = min(100, len(changed_files)*8 + len(touched_modules)*7 + len(impacted)*3 + len(impacted_edges))
    risk = "critical" if score >= 80 or len(touched_modules) >= 8 else "high" if score >= 55 or len(touched_modules) >= 5 else "medium" if score >= 25 else "low"
    reasons = [f"{len(changed_files)} changed files", f"{len(touched_modules)} touched/impacted modules", f"{len(impacted)} impacted nodes within dependency depth 2", f"{len(impacted_edges)} impacted edges"]
    risky_nodes = [node_by_id[i] for i in impacted if i in node_by_id and node_by_id[i].risk_tags]
    if risky_nodes:
        reasons.append("Risk tags touched: " + ", ".join(sorted(set(tag for n in risky_nodes for tag in n.risk_tags))))
    return BlastRadiusReport(changed_files=sorted(changed_files), touched_modules=touched_modules, impacted_nodes=sorted(impacted), impacted_edges=impacted_edges, blast_radius_score=score, risk_level=risk, reasons=reasons)
