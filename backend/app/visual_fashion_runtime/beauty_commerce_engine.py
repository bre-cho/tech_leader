from .schemas import BeautyCommercePlan, VisualDNA, EmotionalPerceptionGraph


class BeautyCommerceEngine:
    def build(self, dna: VisualDNA, graph: EmotionalPerceptionGraph) -> BeautyCommercePlan:
        if "pastel" in dna.archetype:
            return BeautyCommercePlan(
                product_positioning="playful premium fashion identity for Gen Z luxury beauty commerce",
                audience_desire="the viewer wants to become the confident pastel luxury girl, not just buy the product",
                trust_triggers=[
                    "consistent face identity",
                    "high-end hair and skin rendering",
                    "premium accessory clarity",
                    "fashion campaign lighting",
                ],
                conversion_triggers=[
                    "low-angle runway authority",
                    "sunglasses hero close-up",
                    "pastel palette memory",
                    "motion-native social energy",
                ],
                content_angle="identity commerce: sell the fantasy of becoming the character",
            )

        return BeautyCommercePlan(
            product_positioning="quiet luxury K-beauty and jewelry editorial commerce",
            audience_desire="the viewer wants refined beauty, softness, intimacy and premium status",
            trust_triggers=[
                "pearl and jewelry detail",
                "soft realistic skin",
                "clean luxury set",
                "controlled editorial lighting",
            ],
            conversion_triggers=[
                "perfume hero frame",
                "overhead luxury flatlay",
                "glossy hair framing",
                "soft feminine eye contact",
            ],
            content_angle="premium trust commerce: sell elegance, refinement and beauty authority",
        )


beauty_commerce_engine = BeautyCommerceEngine()
