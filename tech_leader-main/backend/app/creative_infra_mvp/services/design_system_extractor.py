from app.creative_infra_mvp.contracts import BusinessInput, DesignSystem

class DesignSystemExtractor:
    def extract(self, business: BusinessInput) -> DesignSystem:
        industry = business.industry.lower()
        premium = any(x in (business.reference_notes or business.brand_name).lower() for x in ["luxury", "premium", "cao cấp"])
        if "beauty" in industry or "cosmetic" in industry or "spa" in industry:
            colors = ["champagne gold", "soft ivory", "warm beige", "clean white"]
            typography = ["elegant serif headline", "clean sans-serif body", "minimal CTA"]
            visual = ["glowing skin", "soft product reflections", "premium beauty close-up"]
        elif "fashion" in industry:
            colors = ["black", "ivory", "champagne", "editorial gray"]
            typography = ["high-fashion serif", "condensed sans-serif"]
            visual = ["editorial silhouette", "fabric realism", "luxury spacing"]
        elif "f&b" in industry or "food" in industry:
            colors = ["warm amber", "earth brown", "cream", "fresh green"]
            typography = ["friendly bold sans-serif", "appetite-driven labels"]
            visual = ["macro food texture", "steam/splash", "warm lifestyle mood"]
        else:
            colors = ["deep navy", "white", "silver", "accent blue"]
            typography = ["bold sans-serif headline", "readable product labels"]
            visual = ["clean product hero", "trust badges", "high contrast CTA"]

        if premium:
            colors = ["black", "champagne gold", "ivory", "soft shadow"]
            visual.append("premium negative space")

        return DesignSystem(
            colors=colors,
            typography=typography,
            spacing={"outer_margin": "8%", "hero_negative_space": "20%", "cta_safe_zone": "bottom third"},
            visual_language=visual,
            composition_rules=[
                "product hero must be visible in first glance",
                "face or emotional trigger anchors attention",
                "CTA must not compete with face/product",
                "layout must preserve typography-safe region",
            ],
            brand_personality={
                "tone": business.reference_notes or "premium, trustworthy, conversion-focused",
                "industry": business.industry,
                "audience": business.audience,
            },
            motion_style={"poster_to_video": "slow product reveal, gaze follows product, CTA end card"},
            trust_style={"signals": ["real texture", "clean lighting", "readable product", "social proof zone"]},
            cta_style={"position": "bottom-right or lower third", "contrast": "high", "copy_rule": "outcome-first"}
        )
