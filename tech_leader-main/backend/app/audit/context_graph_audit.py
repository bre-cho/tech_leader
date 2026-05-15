from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from app.models.records import ContextEntityRecord, ContextRelationRecord
from app.governance.operating_law import REQUIRED_CONTEXT_ENTITIES


class ContextGraphAuditor:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> dict[str, Any]:
        entities = self.db.query(ContextEntityRecord).all()
        relations = self.db.query(ContextRelationRecord).all()

        entity_keys = {e.entity_key for e in entities}
        entity_types = {e.entity_type for e in entities}

        # Missing required entity types
        missing_types = [t for t in REQUIRED_CONTEXT_ENTITIES if t not in entity_types]

        # Orphan entities: appear only in entity table, no relations at all
        rel_keys = set()
        for r in relations:
            rel_keys.add(r.source_key)
            rel_keys.add(r.target_key)
        orphan_nodes = [k for k in entity_keys if k not in rel_keys]

        # Broken edges: relation references key not in entity table
        broken_edges = []
        for r in relations:
            if r.source_key not in entity_keys:
                broken_edges.append({"source_key": r.source_key, "relation_type": r.relation_type, "target_key": r.target_key, "missing": "source"})
            if r.target_key not in entity_keys:
                broken_edges.append({"source_key": r.source_key, "relation_type": r.relation_type, "target_key": r.target_key, "missing": "target"})

        # Cyclic dependency detection (DFS)
        cyclic = self._detect_cycles(relations)

        status = "PASS" if not missing_types and not broken_edges and not cyclic else "FAIL"

        fixes = []
        if missing_types:
            fixes.append(f"Add required entity types: {missing_types}")
        if broken_edges:
            fixes.append(f"Fix {len(broken_edges)} broken relation edge(s)")
        if cyclic:
            fixes.append(f"Resolve {len(cyclic)} cyclic dependency path(s)")

        return {
            "context_graph_status": status,
            "total_entities": len(entities),
            "total_relations": len(relations),
            "missing_nodes": missing_types,
            "orphan_nodes": orphan_nodes[:20],
            "broken_edges": broken_edges[:20],
            "cyclic_dependencies": cyclic[:10],
            "runtime_mismatch": [],
            "recommended_fixes": fixes,
        }

    def _detect_cycles(self, relations) -> list[list[str]]:
        graph: dict[str, list[str]] = {}
        for r in relations:
            graph.setdefault(r.source_key, []).append(r.target_key)

        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])
            path.pop()
            rec_stack.discard(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node, [])

        return cycles
