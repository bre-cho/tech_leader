from __future__ import annotations

from .schemas import Scorecard, StoryboardVariant, CampaignBrief, SellingMechanism, VisualAnalysis, Scene


class StoryboardScorer:
    def score(self, variant: StoryboardVariant, brief: CampaignBrief, mechanism: SellingMechanism, visual: VisualAnalysis, scenes: list[Scene]) -> Scorecard:
        has_hook = any("hook" in s.goal.lower() or "attention" in s.goal.lower() for s in scenes)
        has_proof = any("proof" in s.goal.lower() or "detail" in s.visual.lower() for s in scenes)
        has_close = any("close" in s.goal.lower() or "cta" in s.goal.lower() or "brand" in s.goal.lower() for s in scenes)
        base = 72
        ctr = base + (10 if has_hook else 0) + (8 if variant == StoryboardVariant.viral else 0)
        attention = base + (12 if has_hook else 0) + (6 if visual.confidence > 0.65 else 0)
        trust = base + (12 if has_proof else 0) + (8 if variant == StoryboardVariant.trust else 0)
        conversion = base + (10 if has_close else 0) + (8 if variant == StoryboardVariant.conversion else 0)
        final = round((ctr * 0.25) + (attention * 0.25) + (trust * 0.25) + (conversion * 0.25))
        final = max(0, min(100, final))
        verdict = "SCALE" if final >= 88 else "UPGRADE" if final >= 78 else "REBUILD"
        return Scorecard(
            ctr_score=min(100, ctr),
            attention_score=min(100, attention),
            trust_score=min(100, trust),
            conversion_score=min(100, conversion),
            final_score=final,
            verdict=verdict,
            reasons=[
                f"Variant optimized for {variant.value}.",
                f"Detected mechanism: {mechanism.mechanism}.",
                "Storyboard includes hook, proof, and brand close." if has_hook and has_proof and has_close else "Storyboard needs stronger hook/proof/close coverage.",
            ],
        )
