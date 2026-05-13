import json
from sqlalchemy.orm import Session
from app.models.records import ContextEntityRecord, ContextRelationRecord

class ContextGraphStore:
    def __init__(self, db: Session):
        self.db = db

    def upsert_entity(self, entity_type: str, entity_key: str, payload: dict):
        row = self.db.query(ContextEntityRecord).filter(ContextEntityRecord.entity_key == entity_key).first()
        if row:
            row.payload_json = json.dumps(payload, ensure_ascii=False)
        else:
            row = ContextEntityRecord(entity_type=entity_type, entity_key=entity_key, payload_json=json.dumps(payload, ensure_ascii=False))
            self.db.add(row)
        self.db.commit()
        return row

    def add_relation(self, source_key: str, relation_type: str, target_key: str, payload: dict | None = None):
        row = ContextRelationRecord(source_key=source_key, relation_type=relation_type, target_key=target_key, payload_json=json.dumps(payload or {}, ensure_ascii=False))
        self.db.add(row); self.db.commit(); self.db.refresh(row)
        return row

    def entities(self):
        rows = self.db.query(ContextEntityRecord).order_by(ContextEntityRecord.updated_at.desc()).all()
        return [{"type": r.entity_type, "key": r.entity_key, "payload": json.loads(r.payload_json)} for r in rows]

    def relations(self):
        rows = self.db.query(ContextRelationRecord).order_by(ContextRelationRecord.created_at.desc()).all()
        return [{"source": r.source_key, "relation": r.relation_type, "target": r.target_key, "payload": json.loads(r.payload_json or '{}')} for r in rows]
