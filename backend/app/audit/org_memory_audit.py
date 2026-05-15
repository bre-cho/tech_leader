from __future__ import annotations

import json
from typing import Any
from sqlalchemy.orm import Session
from app.models.records import WinnerDNARecord, DecisionLogRecord


class OrgMemoryAuditor:
    def __init__(self, db: Session):
        self.db = db

    def run(self, max_age_days: int = 90) -> dict[str, Any]:
        from datetime import datetime, timezone, timedelta

        dna_rows = self.db.query(WinnerDNARecord).all()
        decision_rows = self.db.query(DecisionLogRecord).all()

        # Conflicting decisions: same decision_type but different outcomes for same workflow_type
        type_outcomes: dict[str, set[str]] = {}
        for r in decision_rows:
            type_outcomes.setdefault(r.decision_type, set()).add(r.outcome)
        conflicting_decisions = [
            {"decision_type": dt, "outcomes": list(outs)}
            for dt, outs in type_outcomes.items()
            if len(outs) > 1
        ]

        # Outdated winner DNA (older than max_age_days)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        outdated_dna = []
        for r in dna_rows:
            try:
                created = r.created_at
                if hasattr(created, "replace"):
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    if created < cutoff:
                        outdated_dna.append({"industry": r.industry, "visual_type": r.visual_type, "created_at": str(r.created_at)})
            except Exception:
                pass

        # Unversioned memory: decision logs without metadata
        unversioned = [
            r.decision_id
            for r in decision_rows
            if not r.metadata_json or r.metadata_json in ("{}", "null", "")
        ]

        # Memory without source agent
        no_source = [
            r.decision_id
            for r in decision_rows
            if not r.metadata_json
            or "agent_name" not in (r.metadata_json or "")
        ]

        status = "PASS" if not conflicting_decisions and not outdated_dna else "WARN"

        return {
            "org_memory_status": status,
            "total_winner_dna": len(dna_rows),
            "total_decisions": len(decision_rows),
            "conflicting_decisions": conflicting_decisions[:10],
            "outdated_strategy_records": outdated_dna[:10],
            "unversioned_memory_records": unversioned[:10],
            "memory_without_source_agent": no_source[:10],
        }
