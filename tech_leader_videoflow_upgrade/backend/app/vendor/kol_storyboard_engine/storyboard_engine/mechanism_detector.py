from __future__ import annotations

from .schemas import CampaignBrief, SellingMechanism, VisualAnalysis


class VisualMechanismDetector:
    def detect(self, brief: CampaignBrief, visual: VisualAnalysis) -> SellingMechanism:
        industry = brief.industry.lower()
        goal = brief.goal.lower()
        product = brief.product.lower()

        if "fashion" in industry or "sleepwear" in product:
            return SellingMechanism(
                mechanism="desire + identity + detail proof",
                buyer_intent="feel premium, attractive, confident, and self-owned",
                emotional_driver="private confidence and elevated feminine identity",
                proof_driver="fabric texture, lace detail, fit, editorial styling",
                friction_risk="may look too artificial or too sensual if realism is not controlled",
                reason="Fashion poster sells by identity first, then material proof and final brand memory.",
            )
        if "skincare" in industry or "beauty" in industry:
            return SellingMechanism(
                mechanism="trust + visible result + product hero",
                buyer_intent="look healthier, smoother, brighter, and more premium",
                emotional_driver="confidence through visible skin transformation",
                proof_driver="skin texture, serum bottle, ingredient/result cues",
                friction_risk="over-retouched skin can reduce trust",
                reason="Beauty ads need trust before desire, with product proof close to the face.",
            )
        if goal == "conversion":
            mechanism = "problem/desire + product proof + CTA"
        else:
            mechanism = "attention hook + brand memory + soft CTA"
        return SellingMechanism(
            mechanism=mechanism,
            buyer_intent="understand product value quickly",
            emotional_driver="curiosity and relevance",
            proof_driver="product close-up, benefit cue, usage context",
            friction_risk="unclear offer or weak first 3 seconds",
            reason="Generic ad uses fast hook, clear proof, and direct closing frame.",
        )
