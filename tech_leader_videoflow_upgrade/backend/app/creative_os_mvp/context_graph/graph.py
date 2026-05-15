from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Edge:
    source: str
    relation: str
    target: str
    weight: float = 1.0
    evidence: dict[str, Any] = field(default_factory=dict)

class CreativeContextGraph:
    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[Edge] = []
        self.index = defaultdict(list)

    def add_node(self, node_id: str, node_type: str, **attrs):
        self.nodes[node_id] = {"type": node_type, **attrs}
        return node_id

    def add_edge(self, source: str, relation: str, target: str, weight: float = 1.0, **evidence):
        edge = Edge(source, relation, target, weight, evidence)
        self.edges.append(edge)
        self.index[source].append(edge)
        return edge

    @classmethod
    def from_request(cls, req):
        g = cls()
        b = req.brand
        g.add_node("brand", "Brand", name=b.brand_name, dna=b.brand_dna)
        g.add_node("audience", "Audience", description=b.audience)
        g.add_node("product", "Product", name=b.product_name, type=b.product_type)
        g.add_node("campaign", "Campaign", channel=b.channel, objective=b.objective)
        g.add_edge("brand", "targets", "audience")
        g.add_edge("product", "appears_in", "campaign")
        g.add_edge("campaign", "optimizes_for", b.objective or "conversion")
        return g

    def commercial_edges(self):
        return [
            ("face", "anchors", "emotional_attention", .88),
            ("eyes", "retain", "attention", .82),
            ("product_hero", "drives", "desire", .86),
            ("cta", "converts", "intent", .77),
            ("premium_lighting", "increases", "trust", .74),
            ("typography", "increases", "readability", .80),
        ]
