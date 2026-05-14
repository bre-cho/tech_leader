from __future__ import annotations
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .ai_change_visualizer import make_change_markdown
from .architecture_drift_detector import detect_architecture_drift
from .blast_radius_analyzer import analyze_blast_radius
from .code_graph_scanner import scan_repo
from .models import ArchitectureRunReport, CodeGraphSnapshot
from .promotion_gate_guard import promotion_gate

app = typer.Typer(help="Architecture Control Tower — CodeBoarding-style AI patch guard")
console = Console()

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj.model_dump_json(indent=2), encoding="utf-8")

def read_snapshot(path: Path) -> CodeGraphSnapshot:
    return CodeGraphSnapshot.model_validate_json(path.read_text(encoding="utf-8"))

@app.command()
def snapshot(repo: Path = typer.Option(Path("."), "--repo", "-r"), out: Path = typer.Option(Path("runtime/architecture-governance/snapshot.json"), "--out", "-o")):
    snap = scan_repo(repo)
    write_json(out, snap)
    console.print(Panel(f"Snapshot saved: {out}\nNodes={len(snap.nodes)} Edges={len(snap.edges)}", title="Architecture Snapshot"))

@app.command()
def compare(before: Path = typer.Option(..., "--before"), repo: Path = typer.Option(Path("."), "--repo", "-r"), out_dir: Path = typer.Option(Path("runtime/architecture-governance"), "--out-dir")):
    before_snap = read_snapshot(before)
    after_snap = scan_repo(repo)
    blast = analyze_blast_radius(before_snap, after_snap)
    drift = detect_architecture_drift(before_snap, after_snap)
    decision = promotion_gate(blast, drift)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "snapshot_after.json", after_snap)
    write_json(out_dir / "blast_radius_report.json", blast)
    write_json(out_dir / "drift_report.json", drift)
    write_json(out_dir / "promotion_decision.json", decision)
    (out_dir / "change_viewer.md").write_text(make_change_markdown(after_snap, blast, drift), encoding="utf-8")
    report = ArchitectureRunReport(status="ready" if decision.status=="promote" else "manual_review" if decision.status=="manual_review" else "blocked", before_snapshot=before_snap, after_snapshot=after_snap, blast_radius_report=blast, drift_report=drift, promotion_decision=decision, artifacts=[str(out_dir / x) for x in ["snapshot_after.json", "blast_radius_report.json", "drift_report.json", "promotion_decision.json", "change_viewer.md"]])
    write_json(out_dir / "architecture_run_report.json", report)
    table = Table(title="Architecture Control Tower")
    table.add_column("Gate"); table.add_column("Value")
    table.add_row("Promotion", decision.status); table.add_row("Score", str(decision.score)); table.add_row("Blast radius", f"{blast.risk_level} / {blast.blast_radius_score}"); table.add_row("Drift passed", str(drift.passed)); table.add_row("Violations", str(len(drift.violations)))
    console.print(table)
    if decision.status == "block": raise typer.Exit(code=2)
    if decision.status == "manual_review": raise typer.Exit(code=1)

@app.command()
def mermaid(repo: Path = typer.Option(Path("."), "--repo", "-r"), out: Path = typer.Option(Path("runtime/architecture-governance/architecture_graph.md"), "--out")):
    snap = scan_repo(repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(make_change_markdown(snap, None, None), encoding="utf-8")
    console.print(f"Mermaid architecture map written: {out}")

if __name__ == "__main__":
    app()
