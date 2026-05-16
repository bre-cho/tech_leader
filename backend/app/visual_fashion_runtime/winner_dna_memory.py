from .schemas import VisualDNA, BeautyCommercePlan, FashionMotionPlan


class WinnerDNAMemoryBuilder:
    def build(self, dna: VisualDNA, commerce: BeautyCommercePlan, motion: FashionMotionPlan, provider: str) -> dict:
        return {
            "dna_type": "fashion_beauty_visual_winner",
            "archetype": dna.archetype,
            "palette": dna.palette,
            "material_language": dna.material_language,
            "lighting_language": dna.lighting_language,
            "camera_language": dna.camera_language,
            "hair_signature": dna.hair_signature,
            "commerce_angle": commerce.content_angle,
            "motion_style": motion.motion_style,
            "provider": provider,
            "scores": dna.scores,
            "why_this_wins": [
                "strong character continuity",
                "clear luxury perception",
                "motion-ready composition",
                "social commerce identity fantasy",
                "repeatable color and styling system",
            ],
        }


winner_dna_memory_builder = WinnerDNAMemoryBuilder()
