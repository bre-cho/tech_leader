from __future__ import annotations

from typing import Any, Dict
from .schemas import ProjectBible

class ProjectBibleEngine:
    """Builds the 5-part project profile: identity, voice, visual, AEO, rules."""

    def build(self, campaign_brief: Dict[str, Any], poster_analysis: Dict[str, Any] | None = None) -> ProjectBible:
        poster_analysis = poster_analysis or {}
        brand = campaign_brief.get("brand") or "Unknown Brand"
        product = campaign_brief.get("product") or "product"
        industry = campaign_brief.get("industry") or "commercial"
        style = campaign_brief.get("style") or "cinematic commercial"
        colors = poster_analysis.get("colors") or poster_analysis.get("palette") or []
        palette = colors[:5] if isinstance(colors, list) and colors else ["brand primary", "shadow", "warm highlight", "soft neutral", "accent"]
        return ProjectBible(
            project_title=f"{brand.upper()} — CINEMATIC POSTER SAGA",
            core_premise=f"Turn the {industry} poster for {product} into a short cinematic ad built from emotion, tactile proof, and brand memory.",
            pillars=["Hook through immediate visual emotion", "Product proof through tactile detail", "Brand close through identity and sound"],
            narrator_persona="The Premium Brand Narrator",
            voice_direction="cinematic, calm, confident, intimate, with breathable pauses",
            visual_style_base=f"{style}, premium photorealistic commercial cinematography, tactile product detail",
            motion_style="slow push-in, floating camera, macro detail, controlled movement, micro-dynamics only",
            palette=palette,
            aeo_philosophy="Sound-first commercial mix: environment creates realism, foley proves product texture, music supports emotion without overpowering voice.",
            soundscape_layers={
                "environment": "soft studio room tone, subtle air movement, location ambience based on campaign world",
                "foley": "fabric movement, product touch, hand motion, breath, packaging detail",
                "music": "minimal premium cinematic bed, low pulse, elegant restraint"
            },
            negative_guardrails=["no watermark", "no distorted text", "no plastic skin", "no exaggerated anatomy", "no rapid chaotic motion", "no off-brand color palette"]
        )
