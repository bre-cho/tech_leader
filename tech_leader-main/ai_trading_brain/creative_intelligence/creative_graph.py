from __future__ import annotations
from .models import CreativeAsset

class CreativeGraphBuilder:
    def build(self, asset: CreativeAsset) -> dict:
        nodes = [
            {"id": "audience", "label": asset.audience, "kind": "market"},
            {"id": "hook", "label": asset.hook, "kind": "attention"},
            {"id": "offer", "label": asset.offer, "kind": "value"},
            {"id": "style", "label": asset.visual_style, "kind": "visual"},
            {"id": "platform", "label": asset.platform, "kind": "distribution"},
        ]
        edges = [
            {"source": "audience", "target": "hook", "relation": "pain_to_attention"},
            {"source": "hook", "target": "offer", "relation": "attention_to_value"},
            {"source": "offer", "target": "style", "relation": "promise_to_visual_trust"},
            {"source": "style", "target": "platform", "relation": "format_fit"},
        ]
        return {"asset_id": asset.asset_id, "nodes": nodes, "edges": edges}
