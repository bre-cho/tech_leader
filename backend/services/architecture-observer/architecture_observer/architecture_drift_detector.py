from __future__ import annotations
from .models import CodeGraphSnapshot, DriftReport

ALLOWED_LAYER_IMPORTS = {
    "frontend": {"frontend", "library", "docs", "config"},
    "service": {"service", "library", "runtime", "memory", "context_graph", "config"},
    "agent": {"agent", "service", "library", "runtime", "memory", "context_graph", "config"},
    "workflow": {"workflow", "agent", "service", "library", "runtime", "memory", "config"},
    "runtime": {"runtime", "library", "config"},
    "memory": {"memory", "library", "config"},
    "context_graph": {"context_graph", "library", "config"},
    "test": {"frontend", "service", "agent", "workflow", "runtime", "library", "memory", "context_graph", "config", "test"},
    "library": {"library", "config"},
}

def detect_architecture_drift(before: CodeGraphSnapshot | None, after: CodeGraphSnapshot) -> DriftReport:
    node_by_id = {n.id: n for n in after.nodes}
    violations, warnings = [], []
    for edge in after.edges:
        src, dst = node_by_id.get(edge.source), node_by_id.get(edge.target)
        if not src or not dst: continue
        allowed = ALLOWED_LAYER_IMPORTS.get(src.layer)
        if allowed and dst.layer not in allowed:
            violations.append(f"Layer drift: {src.path} ({src.layer}) imports {dst.path} ({dst.layer})")
    risk_summary = after.summary.get("risk_tags", {})
    if risk_summary.get("credential_touch", 0) > 0: warnings.append("Credential-like terms detected. Require secret scanning before promotion.")
    if risk_summary.get("shell_execution", 0) > 0: warnings.append("Shell execution detected. Require safety policy review.")
    if risk_summary.get("database_migration", 0) > 0: warnings.append("Migration/database code touched. Require migration gate.")
    before_layers = before.summary.get("layers", {}) if before else {}
    after_layers = after.summary.get("layers", {})
    layer_drift = {"before": before_layers, "after": after_layers, "delta": {k: after_layers.get(k, 0) - before_layers.get(k, 0) for k in sorted(set(before_layers) | set(after_layers))}}
    before_edges = before.summary.get("edge_count", 0) if before else 0
    after_edges = after.summary.get("edge_count", 0)
    dependency_drift = {"before_edges": before_edges, "after_edges": after_edges, "delta_edges": after_edges - before_edges}
    if before and after_edges > before_edges * 1.25 + 10:
        warnings.append("Dependency edge count grew sharply. Review coupling growth.")
    drift_score = min(100, len(violations)*20 + len(warnings)*8 + max(0, dependency_drift["delta_edges"])//3)
    return DriftReport(passed=len(violations)==0 and drift_score < 65, drift_score=drift_score, violations=violations, warnings=warnings, layer_drift=layer_drift, dependency_drift=dependency_drift)
