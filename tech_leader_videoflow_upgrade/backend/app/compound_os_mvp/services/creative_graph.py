from sqlalchemy.orm import Session
from app.compound_os_mvp.db import GraphEdge
from datetime import datetime

SEED_EDGES = [
    ("layout:minimal", "increases", "trust", 0.72, "minimal layout reduces cognitive load"),
    ("spacing:large", "increases", "premium_perception", 0.75, "large whitespace signals premium editorial design"),
    ("face:close_up", "increases", "emotional_attention", 0.86, "human faces attract first fixation"),
    ("typography:serif", "increases", "luxury_perception", 0.70, "serif typography often signals premium/editorial tone"),
    ("hook:outcome_first", "increases", "conversion", 0.78, "outcome-first hooks clarify value quickly"),
    ("cta:high_contrast", "improves", "click_probability", 0.80, "CTA contrast improves action clarity"),
    ("emotion:warmth", "increases", "engagement", 0.68, "warmth improves approachability"),
    ("campaign:consistent_visual_dna", "increases", "brand_recall", 0.82, "repetition builds memory structures"),
]

class CreativeIntelligenceGraph:
    def ensure_seed(self, db: Session):
        if db.query(GraphEdge).count() == 0:
            for s, r, t, w, e in SEED_EDGES:
                db.add(GraphEdge(source=s, relation=r, target=t, weight=w, evidence=e))
            db.commit()

    def relevant_edges(self, db: Session, industry: str, goal: str, limit=20):
        self.ensure_seed(db)
        edges = db.query(GraphEdge).order_by(GraphEdge.weight.desc()).limit(limit).all()
        return edges

    def reinforce(self, db: Session, source: str, relation: str, target: str, delta: float, evidence: str):
        edge = db.query(GraphEdge).filter_by(source=source, relation=relation, target=target).first()
        if not edge:
            edge = GraphEdge(source=source, relation=relation, target=target, weight=max(0, min(1, 0.5 + delta)), evidence=evidence)
            db.add(edge)
        else:
            edge.weight = max(0, min(1, (edge.weight * edge.observations + (edge.weight + delta)) / (edge.observations + 1)))
            edge.observations += 1
            edge.evidence = evidence
            edge.updated_at = datetime.utcnow()
        db.commit()
        return edge
