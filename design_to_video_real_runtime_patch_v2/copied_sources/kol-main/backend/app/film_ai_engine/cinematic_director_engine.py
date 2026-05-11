from __future__ import annotations
from typing import Any, Dict, List
from .schemas import ProjectBible, ShotBlock, DirectorPassOutput

class CinematicDirectorEngine:
    """Pass 0 assets/lookdev, Pass 1 T2I keyframes, Pass 2 T2V motion prompts."""
    def compile(self, shot_blocks: List[ShotBlock], bible: ProjectBible, providers: List[str] | None = None) -> DirectorPassOutput:
        providers = providers or ["veo", "runway", "kling", "seedance2"]
        assets = self._pass0_assets(bible)
        image_prompts = [self._image_prompt(i, s, bible) for i, s in enumerate(shot_blocks, 1)]
        video_prompts = []
        for i, shot in enumerate(shot_blocks, 1):
            for provider in providers:
                video_prompts.append(self._video_prompt(i, shot, bible, provider))
        return DirectorPassOutput(
            total_shots=len(shot_blocks),
            assets=assets,
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            verification={
                "input_shots": len(shot_blocks),
                "image_outputs": len(image_prompts),
                "video_outputs_per_provider": len(shot_blocks),
                "providers": providers,
                "status": "PASS" if len(image_prompts) == len(shot_blocks) else "FAIL",
                "physics_safeguard": "micro-movements only; no rapid large action"
            }
        )

    def _pass0_assets(self, bible: ProjectBible) -> List[Dict[str, Any]]:
        style = bible.visual_style_base
        return [
            {"prompt_type":"T2I_Asset","asset_category":"brand_world","asset_name":bible.project_title,"prompt":f"Look development board for {bible.project_title}, {style}, palette {', '.join(bible.palette)}, premium texture study, cinematic lighting","visual_notes":"Use as continuity reference."},
            {"prompt_type":"T2I_LookDev_MoodBoard","location_name":"campaign_world","time_of_day":"brand-defined","prompt":f"Mood board: {style}, controlled atmosphere, tactile product/material details, restrained highlights, safe mobile composition","lighting_notes":"Preserve campaign palette and readable subject separation."},
            {"prompt_type":"T2I_Context_Ref","ref_category":"texture","ref_name":"product_material_detail","prompt":f"Macro reference of product material, tactile proof, photorealistic, {style}","relevance_note":"Feeds detail-proof shots and karaoke/emphasis timing."},
        ]

    def _image_prompt(self, n: int, shot: ShotBlock, bible: ProjectBible) -> Dict[str, Any]:
        return {
            "prompt_type":"T2I_Shot_Image",
            "global_shot_number":str(n),
            "source_beat":shot.beat,
            "environment_context":shot.sequence,
            "prompt": f"{shot.camera}. {shot.action} {bible.visual_style_base}. Palette: {', '.join(bible.palette)}. Photorealistic texture, cinematic composition, safe margins.",
            "cinematography_instructions":{"shot_type":shot.scale,"angle":shot.camera,"lens":"commercial prime lens / anamorphic when appropriate"},
            "negative_prompt": ", ".join(bible.negative_guardrails),
        }

    def _video_prompt(self, n: int, shot: ShotBlock, bible: ProjectBible, provider: str) -> Dict[str, Any]:
        veo_payload = {
            "prompt": f"An instruction for animating a static image. SCENE: {shot.action}. MICRO-MOVEMENTS: {shot.micro_movement}; breath, fabric/product texture, light shimmer, subtle particles only. ATMOSPHERE: {shot.lighting}, controlled cinematic mood. Avoid large rapid actions or physics-breaking motion.",
            "style": ["cinematic commercial", "hyperrealistic", "premium lighting", "tactile detail", "slow cinema"],
            "camera_movement": [shot.camera, f"{shot.scale} shot"],
            "audio": {
                "music": bible.soundscape_layers.get("music"),
                "ambient_sound": bible.soundscape_layers.get("environment"),
                "sound_effects": [shot.sfx],
            },
            "negative_prompt": ", ".join(bible.negative_guardrails + ["morphing artifacts", "unrealistic movement", "shaky cam", "subtitles baked into provider output"]),
        }
        return {"prompt_type":"T2V_Shot_Action","provider":provider,"global_shot_number":str(n),"source_beat":shot.beat,"veo_json_payload":veo_payload}
