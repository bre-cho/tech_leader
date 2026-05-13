import time, uuid
from typing import Dict, Any, List

class ContextGraph:
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_type: str, payload: Dict[str, Any]) -> str:
        node_id = f"{node_type}_{uuid.uuid4().hex[:8]}"
        self.nodes.append({"id": node_id, "type": node_type, "payload": payload, "created_at": time.time()})
        return node_id

    def add_edge(self, source: str, relation: str, target: str, weight: float = 1.0):
        self.edges.append({"source": source, "relation": relation, "target": target, "weight": weight})

    def build_for_campaign(self, req: Dict[str, Any]) -> Dict[str, Any]:
        business = self.add_node("BusinessEntity", {"goal": req["business_goal"], "industry": req["industry"]})
        audience = self.add_node("AudienceEntity", {"audience": req["audience"], "platform": req["platform"]})
        offer = self.add_node("OfferEntity", {"product_or_service": req["product_or_service"]})
        campaign = self.add_node("CampaignEntity", {"campaign_type": req["campaign_type"]})
        self.add_edge(business, "targets", audience)
        self.add_edge(offer, "belongs_to", business)
        self.add_edge(campaign, "promotes", offer)
        return {"nodes": self.nodes, "edges": self.edges}
