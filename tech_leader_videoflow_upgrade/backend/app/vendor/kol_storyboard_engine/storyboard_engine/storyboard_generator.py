from __future__ import annotations

import hashlib
from typing import List

from .camera_motion_engine import CameraMotionEngine
from .prompt_compiler import NEGATIVE_DEFAULT, PromptCompiler
from .schemas import CampaignBrief, ProviderName, Scene, SellingMechanism, Storyboard, StoryboardVariant, VisualAnalysis
from .scoring import StoryboardScorer


class StoryboardGenerator:
    def __init__(self) -> None:
        self.camera_engine = CameraMotionEngine()
        self.compiler = PromptCompiler()
        self.scorer = StoryboardScorer()

    def _timeline(self, duration: int) -> list[tuple[str, float, str]]:
        if duration <= 15:
            return [
                ("0-3s", 3, "Hook attention"),
                ("3-6s", 3, "Product reveal"),
                ("6-9s", 3, "Detail proof"),
                ("9-12s", 3, "Emotional transformation"),
                ("12-15s", 3, "Brand close / CTA"),
            ]
        return [
            ("0-3s", 3, "Hook attention"),
            ("3-7s", 4, "Desire setup"),
            ("7-12s", 5, "Product reveal"),
            ("12-18s", 6, "Detail / ingredient proof"),
            ("18-24s", 6, "Lifestyle transformation"),
            ("24-30s", 6, "Brand close / CTA"),
        ]

    def _visual_for_goal(self, brief: CampaignBrief, visual: VisualAnalysis, mechanism: SellingMechanism, goal: str, variant: StoryboardVariant) -> tuple[str, str, str, str | None, str | None]:
        product = brief.product
        brand = brief.brand
        if "Hook" in goal:
            return (
                f"Immediate premium visual hook using {visual.detected_subjects[0] if visual.detected_subjects else 'product hero'} and strong brand mood",
                "Subject enters with confident micro-movement; product mood appears within first second",
                visual.lighting_style,
                "Stop scrolling. Feel the mood." if variant == StoryboardVariant.viral else "A premium moment begins here.",
                brand,
            )
        if "reveal" in goal.lower():
            return (
                f"Reveal {product} as the hero object with premium framing",
                "Camera reveals the product silhouette, fit, texture, or packaging detail",
                visual.lighting_style,
                "Designed to be noticed.",
                product.title(),
            )
        if "proof" in goal.lower() or "detail" in goal.lower() or "ingredient" in goal.lower():
            return (
                f"Macro proof shot showing {', '.join(visual.product_cues[:3])}",
                "Slow detail movement proves material, finish, ingredient, or quality",
                visual.lighting_style,
                "The detail is the difference.",
                "Premium Detail",
            )
        if "transformation" in goal.lower() or "lifestyle" in goal.lower() or "desire" in goal.lower():
            return (
                f"Emotional identity moment showing buyer outcome: {mechanism.emotional_driver}",
                "Subject shifts from stillness into confident controlled movement",
                visual.lighting_style,
                "Not just a product. A state of mind.",
                "Own The Moment",
            )
        return (
            f"Final brand lockup with {brand}, {product}, and clear mobile-safe CTA composition",
            "Hero frame settles into premium poster-like end card",
            visual.lighting_style,
            f"{brand}. Made to be remembered.",
            f"{brand} — Shop Now",
        )

    def generate(self, brief: CampaignBrief, visual: VisualAnalysis, mechanism: SellingMechanism, variant: StoryboardVariant, providers: List[ProviderName]) -> Storyboard:
        timeline = self._timeline(int(brief.duration))
        scenes: list[Scene] = []
        for i, (time_range, seconds, goal) in enumerate(timeline):
            camera, motion = self.camera_engine.plan(variant, i, len(timeline))
            scene_visual, action, lighting, vo, text = self._visual_for_goal(brief, visual, mechanism, goal, variant)
            scene = Scene(
                scene_id=i + 1,
                time_range=time_range,
                duration_seconds=seconds,
                goal=goal,
                visual=scene_visual,
                camera=camera,
                motion=motion,
                lighting=lighting,
                action=action,
                voiceover=vo,
                on_screen_text=text,
                negative_prompt=NEGATIVE_DEFAULT,
            )
            scene.provider_prompts = {p.value: self.compiler.compile_for_provider(p, brief, visual, scene) for p in providers}
            scenes.append(scene)
        scorecard = self.scorer.score(variant, brief, mechanism, visual, scenes)
        sid_base = f"{brief.brand}|{brief.product}|{variant}|{brief.duration}"
        storyboard_id = "sb_" + hashlib.sha1(sid_base.encode()).hexdigest()[:12]
        return Storyboard(
            storyboard_id=storyboard_id,
            variant=variant,
            brief=brief,
            visual_analysis=visual,
            selling_mechanism=mechanism,
            scenes=scenes,
            scorecard=scorecard,
        )
