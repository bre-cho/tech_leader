import json
from sqlalchemy.orm import Session
from app.models.records import WinnerDNARecord
from app.config import settings

class WinnerDNAEngine:
    def __init__(self, db: Session):
        self.db = db

    def recall(self, industry: str, limit: int = 5):
        rows = self.db.query(WinnerDNARecord).filter(WinnerDNARecord.industry.ilike(f"%{industry}%")).order_by(WinnerDNARecord.conversion_score.desc()).limit(limit).all()
        return [json.loads(r.payload_json) for r in rows]

    def list_all(self):
        rows = self.db.query(WinnerDNARecord).order_by(WinnerDNARecord.created_at.desc()).all()
        return [json.loads(r.payload_json) for r in rows]

    def store(self, dna: dict):
        score = float(dna.get("conversion_score", 0))
        if score < settings.winner_dna_threshold:
            return {"stored": False, "reason": f"conversion_score<{settings.winner_dna_threshold}", "dna": dna}
        existing = self.db.query(WinnerDNARecord).filter(
            WinnerDNARecord.industry == dna["industry"],
            WinnerDNARecord.hook == dna["hook"],
        ).first()
        if existing:
            return {"stored": False, "reason": "duplicate_winner_dna", "dna": json.loads(existing.payload_json)}
        row = WinnerDNARecord(
            industry=dna["industry"],
            visual_type=dna["visual_type"],
            hook=dna["hook"],
            offer=dna["offer"],
            conversion_score=score,
            upsell_rate=float(dna.get("upsell_rate", 0)),
            storyboard_pattern=dna["storyboard_pattern"],
            payload_json=json.dumps(dna, ensure_ascii=False),
        )
        self.db.add(row); self.db.commit(); self.db.refresh(row)
        return {"stored": True, "id": row.id, "dna": dna}
