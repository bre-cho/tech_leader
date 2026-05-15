from __future__ import annotations
from .models import CreativeAsset, CreativeScore

class VisualReasoningEngine:
    def score(self, asset: CreativeAsset) -> tuple[CreativeScore, dict]:
        text = " ".join([asset.title, asset.hook, asset.offer, asset.visual_style]).lower()
        attention = 80 + min(15, sum(k in text for k in ["shock", "secret", "before", "after", "fast", "winner"]) * 3)
        trust = 70 + min(20, sum(k in text for k in ["proof", "real", "case", "data", "expert", "luxury"]) * 4)
        clarity = 75 + min(20, sum(bool(getattr(asset, f)) for f in ["hook", "audience", "offer", "visual_style"]) * 4)
        conversion = 72 + min(20, sum(k in text for k in ["offer", "free", "system", "template", "save", "result"]) * 3)
        viral = 65 + min(25, sum(k in text for k in ["trend", "viral", "tiktok", "youtube", "breakout"]) * 4)
        score = CreativeScore(attention, trust, clarity, conversion, viral)
        reasoning = {
            "primary_job": "Biến insight người xem thành hook, hình ảnh và lời hứa dễ hiểu.",
            "improve_next": ["Làm hook cụ thể hơn", "Tăng bằng chứng thị giác", "Đưa CTA rõ hơn"],
            "total_score": score.total,
        }
        return score, reasoning
