
from __future__ import annotations
from app.schemas.hidream import HiDreamGenerateRequest, HiDreamPromptContract

class HiDreamStoryboardExpander:
    def expand(self, req: HiDreamGenerateRequest, contract: HiDreamPromptContract) -> dict:
        if not req.enable_storyboard_expansion:
            return {"enabled": False, "scenes": []}
        product = req.product_name
        return {
            "enabled": True,
            "poster_to_video_intent": "Use HiDream image as premium key visual, then expand into motion-ready product commercial.",
            "scenes": [
                {"scene": 1, "role": "hook", "visual": f"Hero reveal of {product} with cinematic light sweep", "motion": "slow push-in", "duration_sec": 2.5},
                {"scene": 2, "role": "texture", "visual": "Macro material/skin/product texture close-up", "motion": "controlled macro pan", "duration_sec": 3.0},
                {"scene": 3, "role": "benefit", "visual": "Model/product interaction with clear benefit framing", "motion": "natural hand movement and gaze follow", "duration_sec": 4.0},
                {"scene": 4, "role": "proof", "visual": "Before/after or premium result perception", "motion": "split-screen or soft reveal", "duration_sec": 3.0},
                {"scene": 5, "role": "cta", "visual": "Clean end card, product visible, typography-safe background", "motion": "subtle glow and logo lockup", "duration_sec": 2.5},
            ],
            "provider_handoff": {
                "veo": "cinematic commercial, preserve subject and product identity, use scene list as motion plan",
                "kling": "product showcase with natural movement and macro detail",
                "runway": "image-to-video from HiDream key visual with controlled camera motion",
            }
        }
