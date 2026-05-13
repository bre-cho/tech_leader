from app.agents.base import BaseAgent

class OfferAgent(BaseAgent):
    name = "offer-agent"
    required_inputs = ["request", "storyboard"]

    def execute(self, context):
        req = context["request"]
        return [
            {"package": "Starter Motion", "price_hint": "99k", "deliverable": "Ảnh tĩnh → video motion 8s", "best_for": "fanpage/story"},
            {"package": "Ads Video", "price_hint": "199k", "deliverable": "Ảnh tĩnh → video ads 15s", "best_for": req.channel},
            {"package": "Multi Variant", "price_hint": "499k", "deliverable": "1 poster + 3 video variants", "best_for": "A/B testing"},
            {"package": "Full Campaign", "price_hint": "999k", "deliverable": "poster + reel + story + ads video", "best_for": "launch campaign"},
        ]
