from __future__ import annotations

from sqlalchemy.orm import Session
from app.models.records import AgentTrustRecord


class TrustGraphStore:
    def __init__(self, db: Session):
        self.db = db

    def update_agent_trust(self, agent_name: str, confidence: float):
        value = max(0.0, min(1.0, float(confidence)))
        row = self.db.query(AgentTrustRecord).filter(AgentTrustRecord.agent_name == agent_name).first()
        if row:
            total = (row.trust_score * row.sample_count) + value
            row.sample_count += 1
            row.trust_score = total / row.sample_count
        else:
            row = AgentTrustRecord(agent_name=agent_name, trust_score=value, sample_count=1)
            self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return {"agent_name": row.agent_name, "trust_score": row.trust_score, "sample_count": row.sample_count}

    def get_agent_trust(self, agent_name: str):
        row = self.db.query(AgentTrustRecord).filter(AgentTrustRecord.agent_name == agent_name).first()
        if not row:
            return {"agent_name": agent_name, "trust_score": 0.0, "sample_count": 0}
        return {"agent_name": row.agent_name, "trust_score": row.trust_score, "sample_count": row.sample_count}

    def list_agent_trust(self, limit: int = 50):
        rows = self.db.query(AgentTrustRecord).order_by(AgentTrustRecord.trust_score.desc()).limit(limit).all()
        return [{"agent_name": r.agent_name, "trust_score": r.trust_score, "sample_count": r.sample_count} for r in rows]
