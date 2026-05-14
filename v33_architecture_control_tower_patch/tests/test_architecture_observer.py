from pathlib import Path
from architecture_observer.blast_radius_analyzer import analyze_blast_radius
from architecture_observer.architecture_drift_detector import detect_architecture_drift
from architecture_observer.code_graph_scanner import scan_repo
from architecture_observer.promotion_gate_guard import promotion_gate

def test_architecture_observer_snapshot_and_compare(tmp_path: Path):
    (tmp_path / "services" / "api").mkdir(parents=True)
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "util.ts").write_text("export function ok() { return true }\n", encoding="utf-8")
    (tmp_path / "services" / "api" / "route.ts").write_text('import { ok } from "../../lib/util"\nexport const x = ok()\n', encoding="utf-8")
    before = scan_repo(tmp_path)
    assert before.summary["node_count"] == 2
    (tmp_path / "services" / "api" / "route.ts").write_text('import { ok } from "../../lib/util"\nconst secret = "api_key"\nexport const x = ok()\n', encoding="utf-8")
    after = scan_repo(tmp_path)
    blast = analyze_blast_radius(before, after)
    drift = detect_architecture_drift(before, after)
    decision = promotion_gate(blast, drift)
    assert blast.changed_files
    assert drift.warnings
    assert decision.status in {"promote", "manual_review", "block"}
