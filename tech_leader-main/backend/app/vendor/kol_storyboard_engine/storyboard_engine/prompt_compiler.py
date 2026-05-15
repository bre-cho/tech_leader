from __future__ import annotations

from .schemas import CampaignBrief, ProviderName, Scene, VisualAnalysis


NEGATIVE_DEFAULT = "no watermark, no distorted text, no plastic skin, no exaggerated proportions, no cropped subject, no low quality, no extra fingers, no broken anatomy"


class PromptCompiler:
    def build_base_prompt(self, brief: CampaignBrief, visual: VisualAnalysis, scene: Scene) -> str:
        cues = ", ".join(visual.product_cues[:6])
        palette = ", ".join(visual.color_palette[:5])
        return (
            f"Create a cinematic {brief.style} short video ad scene for brand {brief.brand}. "
            f"Product: {brief.product}. Industry: {brief.industry}. Scene goal: {scene.goal}. "
            f"Visual: {scene.visual}. Action: {scene.action}. Camera: {scene.camera}. Motion: {scene.motion}. "
            f"Lighting: {scene.lighting}. Background: {visual.background_style}. Palette: {palette}. "
            f"Product cues: {cues}. Composition: {visual.composition}. "
            f"Keep realistic commercial quality, premium detail, safe margins for mobile vertical ads."
        )

    def compile_for_provider(self, provider: ProviderName, brief: CampaignBrief, visual: VisualAnalysis, scene: Scene) -> dict:
        prompt = self.build_base_prompt(brief, visual, scene)
        common = {
            "provider": provider.value,
            "aspect_ratio": brief.aspect_ratio,
            "duration": scene.duration_seconds,
            "prompt": prompt,
            "negative_prompt": scene.negative_prompt,
        }
        if provider == ProviderName.veo:
            return {**common, "mode": "text_to_video", "camera_control": scene.motion}
        if provider == ProviderName.runway:
            return {**common, "model": "gen_video", "seed_behavior": "optional"}
        if provider == ProviderName.kling:
            return {**common, "mode": "image_to_video_or_text_to_video", "cfg_scale": 0.6}
        if provider == ProviderName.seedance:
            return {**common, "mode": "text_to_video", "motion_strength": "medium"}
        return common
