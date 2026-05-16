"""
V33 — Architecture Control Tower API Routes

Expose architecture-observer CLI as FastAPI endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import sys
import os

# Add backend services to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "services"))

try:
    from architecture_observer.code_graph_scanner import scan_repo
    from architecture_observer.blast_radius_analyzer import analyze_blast_radius
    from architecture_observer.architecture_drift_detector import detect_architecture_drift
    from architecture_observer.promotion_gate_guard import promotion_gate
    from architecture_observer.models import CodeGraphSnapshot
    _ARCH_OBSERVER_AVAILABLE = True
except ImportError:
    _ARCH_OBSERVER_AVAILABLE = False
    scan_repo = analyze_blast_radius = detect_architecture_drift = promotion_gate = CodeGraphSnapshot = None

router = APIRouter(tags=["architecture-control-tower"])
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
GOVERNANCE_DIR = REPO_ROOT / "backend" / "runtime" / "architecture-governance"


class ArchitectureSnapshotRequest(BaseModel):
    """Request to capture current code architecture"""
    pass


class ArchitectureCompareRequest(BaseModel):
    """Request to compare before/after architecture snapshots"""
    before_snapshot_path: str = "backend/runtime/architecture-governance/snapshot_before.json"


@router.post("/architecture/snapshot")
async def take_snapshot(req: ArchitectureSnapshotRequest):
    """
    Capture CodeGraph snapshot of current repository state.
    Stores in runtime/architecture-governance/snapshot.json
    """
    try:
        GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
        snap = scan_repo(REPO_ROOT)
        snapshot_file = GOVERNANCE_DIR / "snapshot_current.json"
        snapshot_file.write_text(snap.model_dump_json(indent=2), encoding="utf-8")
        return {
            "ok": True,
            "snapshot": {
                "nodes": len(snap.nodes),
                "edges": len(snap.edges),
                "path": str(snapshot_file),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snapshot failed: {str(e)}")


@router.post("/architecture/compare")
async def compare_architecture(req: ArchitectureCompareRequest):
    """
    Compare before/after architecture snapshots.
    Returns blast radius, drift analysis, and promotion gate decision.
    """
    try:
        before_file = REPO_ROOT / req.before_snapshot_path
        if not before_file.exists():
            raise ValueError(f"Before snapshot not found: {before_file}")
        
        # Load before snapshot
        before_data = json.loads(before_file.read_text(encoding="utf-8"))
        before_snap = CodeGraphSnapshot.model_validate(before_data)
        
        # Get after snapshot
        after_snap = scan_repo(REPO_ROOT)
        
        # Analyze blast radius and drift
        blast = analyze_blast_radius(before_snap, after_snap)
        drift = detect_architecture_drift(before_snap, after_snap)
        decision = promotion_gate(blast, drift)
        
        # Save reports
        GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
        (GOVERNANCE_DIR / "snapshot_after.json").write_text(after_snap.model_dump_json(indent=2), encoding="utf-8")
        (GOVERNANCE_DIR / "blast_radius_report.json").write_text(blast.model_dump_json(indent=2), encoding="utf-8")
        (GOVERNANCE_DIR / "drift_report.json").write_text(drift.model_dump_json(indent=2), encoding="utf-8")
        (GOVERNANCE_DIR / "promotion_decision.json").write_text(decision.model_dump_json(indent=2), encoding="utf-8")
        
        return {
            "ok": True,
            "promotion_status": decision.status,
            "score": decision.score,
            "blast_radius": {
                "risk_level": blast.risk_level,
                "score": blast.blast_radius_score,
            },
            "drift_check": {
                "passed": drift.passed,
                "violations": len(drift.violations),
            },
            "artifacts": {
                "snapshot_after": str(GOVERNANCE_DIR / "snapshot_after.json"),
                "blast_radius_report": str(GOVERNANCE_DIR / "blast_radius_report.json"),
                "drift_report": str(GOVERNANCE_DIR / "drift_report.json"),
                "promotion_decision": str(GOVERNANCE_DIR / "promotion_decision.json"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/architecture/health")
async def architecture_health():
    """Check if Architecture Control Tower is ready"""
    try:
        snap = scan_repo(REPO_ROOT)
        return {
            "ok": True,
            "status": "architecture-control-tower-ready",
            "nodes": len(snap.nodes),
            "edges": len(snap.edges),
        }
    except Exception as e:
        return {
            "ok": False,
            "status": "architecture-control-tower-error",
            "error": str(e),
        }
