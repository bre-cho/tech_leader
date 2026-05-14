from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.audit.orchestrator import AuditOrchestrator
from app.audit.context_graph_audit import ContextGraphAuditor
from app.audit.memory_audit import MemoryAuditor

router = APIRouter(tags=["audit"])


@router.post("/audit/run")
def run_full_audit(db: Session = Depends(get_db)):
    """Run the complete system audit and return a SystemAuditReport."""
    report = AuditOrchestrator(db).run()
    return report.model_dump()


@router.get("/audit/release-gate")
def get_release_gate(db: Session = Depends(get_db)):
    """Return only the GO / NO-GO release gate decision."""
    report = AuditOrchestrator(db).run()
    return {
        "status": report.release_gate.status,
        "reason": report.release_gate.reason,
        "blocking_failures": report.release_gate.blocking_failures,
        "overall_health_score": report.executive_summary.overall_health_score,
    }


@router.get("/audit/context-graph")
def get_context_graph_audit(db: Session = Depends(get_db)):
    """Return the context graph integrity audit."""
    return ContextGraphAuditor(db).run()


@router.get("/audit/memory")
def get_memory_audit():
    """Return the memory topology audit."""
    return MemoryAuditor().run()
