from .schemas import VisualDNA


class VisualDNAExtractor:
    def extract(self, brief: str) -> VisualDNA:
        text = brief.lower()

        is_pastel_motion = any(k in text for k in ["pastel", "lavender", "peach", "miu", "gen z", "fashion motion", "runway"])
        is_quiet_luxury = any(k in text for k in ["chanel", "quiet luxury", "pearl", "brown", "perfume", "jewelry", "cream"])

        if is_pastel_motion:
            return VisualDNA(
                archetype="hyper_feminine_pastel_fashion_motion",
                palette=["peach", "lavender", "pastel pink", "cream white", "glossy black hair"],
                material_language=["soft knit", "lace", "pleated skirt", "patent leather", "pearl accessories"],
                lighting_language="soft peach-lavender gradient lighting with beauty skin glow",
                camera_language=["low-angle fashion walk", "close-up sunglasses hero", "radial motion background", "orbit skirt spin", "overhead floating editorial"],
                hair_signature="glossy black hair with strong wind-sweep motion and soft wave continuity",
                luxury_signals=["designer-inspired accessories", "pearl necklace", "pastel handbag", "fashion eyewear", "youthful luxury styling"],
                motion_signals=["hair sweep", "jacket flare", "skirt spin", "runway stride", "kinetic diagonal body line"],
                commerce_angle="playful luxury identity commerce for TikTok, Reels and Xiaohongshu",
                scores={
                    "luxury_perception": 9.6,
                    "motion_readiness": 9.8,
                    "social_virality": 9.8,
                    "character_continuity": 9.7,
                    "commerce_conversion": 9.5,
                },
            )

        if is_quiet_luxury:
            return VisualDNA(
                archetype="quiet_luxury_kbeauty_editorial",
                palette=["cream white", "chocolate brown", "champagne gold", "pearl silver", "soft ivory"],
                material_language=["satin", "leather", "pearls", "glossy hair", "soft skin", "white flowers"],
                lighting_language="soft directional editorial beauty lighting with high diffusion and subtle specular highlights",
                camera_language=["overhead luxury flatlay", "85mm intimate portrait", "soft kneeling composition", "jewelry macro", "perfume hero close-up"],
                hair_signature="deep espresso black soft luxury waves with glossy S-curve framing",
                luxury_signals=["pearl jewelry", "leather bags", "perfume bottle", "champagne glass", "flower styling", "jewelry box"],
                motion_signals=["slow hair flow", "soft hand movement", "overhead floating composition", "luxury stillness"],
                commerce_angle="quiet luxury beauty commerce for perfume, jewelry, skincare and premium K-beauty",
                scores={
                    "luxury_perception": 9.8,
                    "motion_readiness": 9.2,
                    "social_virality": 9.3,
                    "character_continuity": 9.7,
                    "commerce_conversion": 9.6,
                },
            )

        return VisualDNA(
            archetype="cinematic_kbeauty_fashion_commerce",
            palette=["cream", "peach", "lavender", "brown", "gold"],
            material_language=["soft fabric", "glossy hair", "jewelry", "premium accessories"],
            lighting_language="cinematic commercial beauty lighting",
            camera_language=["beauty close-up", "fashion medium shot", "product hero", "motion transition"],
            hair_signature="consistent glossy black hair with controlled movement",
            luxury_signals=["jewelry", "premium styling", "clean background"],
            motion_signals=["soft fashion motion", "hair movement", "pose transition"],
            commerce_angle="AI-native fashion beauty commerce",
            scores={
                "luxury_perception": 9.1,
                "motion_readiness": 9.0,
                "social_virality": 9.0,
                "character_continuity": 9.2,
                "commerce_conversion": 9.0,
            },
        )


visual_dna_extractor = VisualDNAExtractor()
