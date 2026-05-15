from __future__ import annotations
from collections import defaultdict, deque
from .models import CodeGraphSnapshot

def reverse_adjacency(snapshot: CodeGraphSnapshot):
    rev = defaultdict(list)
    for edge in snapshot.edges:
        rev[edge.target].append(edge.source)
    return dict(rev)

def affected_by(snapshot: CodeGraphSnapshot, changed_node_ids: list[str], depth: int = 2) -> set[str]:
    rev = reverse_adjacency(snapshot)
    seen = set(changed_node_ids)
    q = deque((node, 0) for node in changed_node_ids)
    while q:
        node, d = q.popleft()
        if d >= depth: continue
        for parent in rev.get(node, []):
            if parent not in seen:
                seen.add(parent)
                q.append((parent, d + 1))
    return seen
