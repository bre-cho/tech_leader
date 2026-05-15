from __future__ import annotations

from .schemas import CampaignBrief, VisualAnalysis


class PosterAnalyzer:
    """MVP-safe analyzer.

    Production hook: replace analyze() body with OpenAI Vision / Gemini Vision / internal CV.
    The current implementation is deterministic and brief-aware so it works without external keys.
    """

    def analyze(self, brief: CampaignBrief, poster_image_url: str | None = None, poster_image_base64: str | None = None) -> VisualAnalysis:
        industry = brief.industry.lower()
        style = brief.style.lower()
        subjects = []
        product_cues = [brief.product]
        palette = []

        if "fashion" in industry or "sleepwear" in brief.product.lower():
            subjects = ["female model", "fashion pose", "fabric detail", "brand title area"]
            product_cues += ["lace texture", "premium fabric", "editorial silhouette"]
            palette = ["black", "deep red", "warm gold"]
            lighting = "warm golden cinematic studio lighting with rim light"
            background = "dark premium editorial studio"
            composition = "model-led luxury poster with product detail close-ups"
        elif "skincare" in industry or "beauty" in industry:
            subjects = ["model face", "serum bottle", "glowing skin", "clean typography area"]
            product_cues += ["skin glow", "premium bottle", "golden particles"]
            palette = ["champagne", "gold", "soft cream"]
            lighting = "soft beauty key light with champagne highlights"
            background = "minimal premium beauty background"
            composition = "close-up model and product hero composition"
        else:
            subjects = ["product hero", "brand area", "supporting visual elements"]
            product_cues += ["packaging", "benefit cue", "detail proof"]
            palette = ["brand primary", "brand accent", "neutral background"]
            lighting = "commercial studio lighting"
            background = "clean advertising background"
            composition = "product-dominant ad layout"

        if "luxury" in style:
            palette.append("premium neutral")

        return VisualAnalysis(
            detected_subjects=subjects,
            product_cues=list(dict.fromkeys(product_cues)),
            color_palette=list(dict.fromkeys(palette)),
            lighting_style=lighting,
            background_style=background,
            composition=composition,
            typography_cues=[brief.brand, "minimal premium text", "safe title lockup"],
            confidence=0.72 if poster_image_url or poster_image_base64 else 0.58,
            raw={"mode": "brief_aware_mvp", "has_image": bool(poster_image_url or poster_image_base64)},
        )
