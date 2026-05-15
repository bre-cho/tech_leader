from __future__ import annotations
from .schemas import CinematicRequest, ShotTechnique
from .technique_library import build_150_technique_library

def select_techniques(req: CinematicRequest, count: int = 6) -> list[ShotTechnique]:
    lib = build_150_technique_library()
    goal = (req.campaign_brief.get("goal") or "").lower()
    product = (req.campaign_brief.get("product") or req.subject_type or "").lower()
    emotion = req.emotion_intent
    scored = []
    for t in lib:
        score = 0
        if emotion in t.family or emotion in t.emotional_effect:
            score += 5
        if any(tag in product for tag in t.best_for):
            score += 3
        if "conversion" in goal and t.family in {"conversion","trust","luxury"}:
            score += 3
        if "attention" in goal and t.family in {"viral_energy","hook","power"}:
            score += 3
        if req.include_viral_hook and t.family in {"viral_energy","hook"}:
            score += 2
        if req.include_multi_angle and t.technique_id in {"orbit_180_product","low_angle_hero","extreme_macro_texture"}:
            score += 2
        scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [x[1] for x in scored[:count]]
    by_id = {t.technique_id: t for t in lib}
    for must in ["extreme_macro_texture", "cta_static_lockup"]:
        if must in by_id and all(s.technique_id != must for s in selected):
            selected.append(by_id[must])
    return selected[:count]
