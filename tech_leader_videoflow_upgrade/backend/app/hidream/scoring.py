
from __future__ import annotations
from typing import List
from app.schemas.hidream import HiDreamGenerateRequest, HiDreamPromptContract, HiDreamScore

class CommercialPerceptionScorer:
    """Business-aware scoring from contract features.

    In production, this can be replaced/augmented by CLIP/vision model QA, CTR model,
    OCR checks, face/product validators, and human feedback. This MVP still computes
    deterministic, explainable scores from prompt and contract quality.
    """
    def score(self, req: HiDreamGenerateRequest, contract: HiDreamPromptContract) -> HiDreamScore:
        prompt = contract.positive_prompt.lower()
        reasons: List[str] = []
        def has(words): return any(w in prompt for w in words)
        luxury = 70 + 8*has(["luxury", "premium", "editorial"]) + 6*has(["champagne", "gold", "commercial"])
        texture = 72 + 10*has(["texture", "pores", "fabric", "glass", "metal", "liquid"])
        typography = 65 + (22 if req.enable_typography_safe_mode else 5) + (4 if req.copy_text else 0)
        adherence = 72 + min(15, len(req.business_goal.split())/2) + 5*bool(req.brand_dna)
        storyboard = 68 + (15 if req.enable_storyboard_expansion else 0) + 8*has(["motion", "storyboard", "keyframe"])
        commercial = (luxury*0.22 + texture*0.18 + typography*0.20 + adherence*0.20 + storyboard*0.20)
        vals = [commercial, luxury, texture, typography, adherence, storyboard]
        vals = [round(max(0, min(100, v)), 2) for v in vals]
        if vals[0] >= 85: reasons.append("High commercial readiness for premium rendering.")
        if vals[2] >= 82: reasons.append("Material and texture instructions are strong.")
        if vals[3] >= 82: reasons.append("Typography-safe policy is enabled for poster workflows.")
        if vals[5] >= 82: reasons.append("Image can expand into storyboard/video keyframes.")
        if not reasons: reasons.append("Usable draft; improve brand DNA, material instructions, and typography-safe layout for better score.")
        return HiDreamScore(
            commercial_score=vals[0], luxury_score=vals[1], texture_score=vals[2], typography_score=vals[3],
            prompt_adherence_score=vals[4], storyboard_readiness_score=vals[5], winner_candidate=vals[0] >= 85, reasons=reasons
        )
