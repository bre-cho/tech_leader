from __future__ import annotations
from .schemas import CinematicRequest, CinematicScenePlan, ShotTechnique

def build_cinematic_prompt(req: CinematicRequest, technique: ShotTechnique, goal: str) -> str:
    brand = req.campaign_brief.get("brand", "the brand")
    product = req.campaign_brief.get("product", req.subject_type)
    style = req.campaign_brief.get("style", "cinematic commercial")
    return (
        f"Create a professional AI video scene for {brand}, featuring {product}. "
        f"GOAL: {goal}. SHOT: {technique.shot_type}. LENS: {technique.lens}. "
        f"CAMERA: {technique.camera_motion}. TECHNIQUE: {technique.name}. "
        f"COMPOSITION: {technique.prompt_fragment}; reserve mobile subtitle safe zone; keep product/subject clearly visible. "
        f"LIGHTING: premium commercial lighting, realistic reflections, controlled highlights, cinematic depth. "
        f"MOTION: natural micro-motions, parallax, cloth/hair/reflection movement where appropriate. "
        f"EMOTION: {technique.emotional_effect}. STYLE: {style}. "
        f"CONSTRAINTS: no morphing, no warped logo, no wrong product identity, no unreadable text, no watermark."
    )

def compile_provider_payloads(req: CinematicRequest, scene: CinematicScenePlan) -> list[dict]:
    payloads = []
    for provider in req.providers:
        if provider == "seedance2":
            payloads.append({"provider":"seedance2","mode":"image_to_video" if req.poster_image_url else "text_to_video","aspect_ratio":req.aspect_ratio,"duration":3,"prompt":scene.cinematic_prompt,"camera":scene.selected_technique.camera_motion,"hook_first":True,"negative_prompt":"morphing, unstable product identity, distorted text, watermark"})
        elif provider == "veo":
            payloads.append({"provider":"veo","mode":"image_to_video" if req.poster_image_url else "text_to_video","aspect_ratio":req.aspect_ratio,"duration":3,"veo_json_payload":{"prompt":scene.cinematic_prompt,"style":["cinematic commercial","realistic","premium lighting"],"camera_movement":[scene.selected_technique.camera_motion, scene.selected_technique.shot_type],"negative_prompt":"morphing, distorted features, unstable logo, watermark"}})
        elif provider == "runway":
            payloads.append({"provider":"runway","mode":"image_to_video","aspect_ratio":req.aspect_ratio,"duration":3,"promptText":scene.cinematic_prompt})
        elif provider == "kling":
            payloads.append({"provider":"kling","mode":"image_to_video","aspect_ratio":req.aspect_ratio,"duration":3,"prompt":scene.cinematic_prompt,"motion_strength":"medium"})
        elif provider == "html_motion":
            payloads.append({"provider":"html_motion","mode":"deterministic_scene","aspect_ratio":req.aspect_ratio,"duration":3,"template":scene.selected_technique.family,"camera_motion":scene.selected_technique.camera_motion})
    return payloads
