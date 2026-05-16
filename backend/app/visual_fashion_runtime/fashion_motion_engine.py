from .schemas import FashionMotionPlan, VisualDNA


class FashionMotionEngine:
    def build(self, dna: VisualDNA) -> FashionMotionPlan:
        if "pastel" in dna.archetype:
            return FashionMotionPlan(
                motion_style="kinetic pastel runway motion with playful luxury confidence",
                camera_rhythm=[
                    "low-angle runway push-in",
                    "hair-sweep whip transition",
                    "sunglasses close-up lock",
                    "skirt spin orbit",
                    "floating overhead fashion tableau",
                ],
                pose_sequence=[
                    "strong forward stride",
                    "sunglasses adjustment",
                    "wall lean with crossed legs",
                    "jacket flare diagonal pose",
                    "skirt spin with handbag swing",
                    "low squat fashion pose",
                    "soft portrait glance",
                ],
                hair_motion="strong wind-swept glossy black hair with readable strand flow",
                cloth_motion="cardigan flare, pleated skirt spin, soft lace movement",
            )

        return FashionMotionPlan(
            motion_style="quiet luxury slow editorial motion",
            camera_rhythm=[
                "slow overhead drift",
                "soft 85mm push-in",
                "jewelry macro insert",
                "handbag product reveal",
                "perfume close-up",
            ],
            pose_sequence=[
                "soft kneeling luxury pose",
                "over-shoulder glance",
                "floor recline editorial",
                "overhead floating hair composition",
                "perfume hero portrait",
            ],
            hair_motion="slow glossy S-curve hair flow with controlled softness",
            cloth_motion="satin and blazer movement kept subtle and premium",
        )


fashion_motion_engine = FashionMotionEngine()
