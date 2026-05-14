import json
from sqlalchemy import or_
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
        source_exists = self.db.query(ContextEntityRecord.id).filter(ContextEntityRecord.entity_key == source_key).first()
        target_exists = self.db.query(ContextEntityRecord.id).filter(ContextEntityRecord.entity_key == target_key).first()
        if not source_exists or not target_exists:
            raise ValueError("context_relation_orphan_blocked")
        row = self.db.query(ContextRelationRecord).filter(
            ContextRelationRecord.source_key == source_key,
            ContextRelationRecord.relation_type == relation_type,
            ContextRelationRecord.target_key == target_key,
        ).first()
        if row:
            row.payload_json = json.dumps(payload or {}, ensure_ascii=False)
            self.db.commit()
            self.db.refresh(row)
            return row
        row = ContextRelationRecord(source_key=source_key, relation_type=relation_type, target_key=target_key, payload_json=json.dumps(payload or {}, ensure_ascii=False))
        self.db.add(row); self.db.commit(); self.db.refresh(row)
        return row

    def entities(self):
        rows = self.db.query(ContextEntityRecord).order_by(ContextEntityRecord.updated_at.desc()).all()
        return [{"type": r.entity_type, "key": r.entity_key, "payload": json.loads(r.payload_json)} for r in rows]

    def relations(self):
        rows = self.db.query(ContextRelationRecord).order_by(ContextRelationRecord.created_at.desc()).all()
        return [{"source": r.source_key, "relation": r.relation_type, "target": r.target_key, "payload": json.loads(r.payload_json or '{}')} for r in rows]

    def neighborhood(self, entity_key: str):
        rels = self.db.query(ContextRelationRecord).filter(
            (ContextRelationRecord.source_key == entity_key) | (ContextRelationRecord.target_key == entity_key)
        ).all()
        node_keys = {entity_key}
        for r in rels:
            node_keys.add(r.source_key)
            node_keys.add(r.target_key)
        entities = self.db.query(ContextEntityRecord).filter(ContextEntityRecord.entity_key.in_(node_keys)).all() if node_keys else []
        return {
            "center": entity_key,
            "entities": [{"type": e.entity_type, "key": e.entity_key, "payload": json.loads(e.payload_json)} for e in entities],
            "relations": [{"source": r.source_key, "relation": r.relation_type, "target": r.target_key, "payload": json.loads(r.payload_json or "{}")} for r in rels],
        }

    def subgraph(self, entity_type: str):
        entities = self.db.query(ContextEntityRecord).filter(ContextEntityRecord.entity_type == entity_type).all()
        keys = [e.entity_key for e in entities]
        if not keys:
            return {"entity_type": entity_type, "entities": [], "relations": []}
        rels = self.db.query(ContextRelationRecord).filter(
            or_(ContextRelationRecord.source_key.in_(keys), ContextRelationRecord.target_key.in_(keys))
        ).all()
        return {
            "entity_type": entity_type,
            "entities": [{"type": e.entity_type, "key": e.entity_key, "payload": json.loads(e.payload_json)} for e in entities],
            "relations": [{"source": r.source_key, "relation": r.relation_type, "target": r.target_key, "payload": json.loads(r.payload_json or "{}")} for r in rels],
        }

    def path(self, source_key: str, target_key: str, max_depth: int = 4):
        if source_key == target_key:
            return {"source": source_key, "target": target_key, "path": [source_key]}
        adjacency: dict[str, list[str]] = {}
        rels = self.db.query(ContextRelationRecord).all()
        for rel in rels:
            adjacency.setdefault(rel.source_key, []).append(rel.target_key)
        queue = [(source_key, [source_key])]
        visited = {source_key}
        while queue:
            node, path = queue.pop(0)
            if len(path) > max_depth + 1:
                continue
            for nxt in adjacency.get(node, []):
                if nxt == target_key:
                    return {"source": source_key, "target": target_key, "path": path + [nxt]}
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return {"source": source_key, "target": target_key, "path": []}
