from __future__ import annotations
import csv, pathlib
from app.ads_engine.schemas.contracts import HookCandidate
DATA_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "hook_templates_1000.csv"

class HookEngine:
    def __init__(self, data_path=DATA_PATH):
        self.rows = list(csv.DictReader(open(data_path, "r", encoding="utf-8")))

    def score_hook(self, hook, pain_points, benefits, proof_points):
        score = 50.0; text = hook.lower()
        if "?" in hook: score += 8
        if any(p.lower() in text for p in pain_points): score += 12
        if any(b.lower() in text for b in benefits): score += 10
        if any(p.lower() in text for p in proof_points): score += 10
        if any(t in text for t in ["7 ngày","50%","trước/sau","30 giây","viral","đối thủ"]): score += 8
        if len(hook.split()) <= 12: score += 6
        return min(score, 99.0)

    def generate(self, industry, pain_points, benefits, proof_points, limit=15):
        candidates = [r for r in self.rows if r["industry"] == industry] or self.rows
        scored = []
        for r in candidates:
            s = self.score_hook(r["hook"], pain_points, benefits, proof_points)
            scored.append(HookCandidate(hook_id=r["hook_id"], hook=r["hook"], industry=r["industry"], formula=r["formula"], intent=r["intent"], emotion=r["emotion"], score=s))
        return sorted(scored, key=lambda x: x.score, reverse=True)[:limit]
