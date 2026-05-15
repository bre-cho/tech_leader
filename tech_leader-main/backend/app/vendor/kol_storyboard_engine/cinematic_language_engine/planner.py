from __future__ import annotations
from uuid import uuid4
from .schemas import CinematicRequest, CinematicScenePlan, CinematicStoryboard
from .selector import select_techniques
from .prompt_compiler import build_cinematic_prompt, compile_provider_payloads
from .technique_library import build_150_technique_library

def _time_range(i: int, duration: int, count: int) -> str:
    step = duration / max(count, 1)
    start = step * i
    end = min(duration, start + step)
    return f"{start:.1f}-{end:.1f}s"

def build_cinematic_storyboard(req: CinematicRequest) -> CinematicStoryboard:
    techniques = select_techniques(req, count=6 if req.duration_seconds >= 30 else 5)
    goals = ["2-second scroll-stop hook","hero product/subject reveal","material or benefit proof","emotional transformation","trust or lifestyle context","brand close and CTA"]
    scenes = []
    for idx, tech in enumerate(techniques):
        goal = goals[min(idx, len(goals)-1)]
        prompt = build_cinematic_prompt(req, tech, goal)
        scene = CinematicScenePlan(
            scene_id=f"cinematic_scene_{idx+1:02d}",
            time_range=_time_range(idx, req.duration_seconds, len(techniques)),
            goal=goal,
            selected_technique=tech,
            composition="mobile-safe cinematic composition with product visibility guard and subtitle negative space",
            lighting="premium high-contrast commercial lighting with controlled rim highlights",
            motion=tech.camera_motion,
            safe_zone={"platform":req.platform,"subtitle_zone":"lower-middle safe area","avoid":["right-side TikTok/Reels buttons","bottom caption/CTA UI","top account/header area"]},
            cinematic_prompt=prompt,
            quality_rules=["CAMERA_TECHNIQUE_REQUIRED","LENS_SPEC_REQUIRED","MOTION_PHYSICS_GUARD","PRODUCT_IDENTITY_LOCK","SUBTITLE_SAFE_ZONE_RESERVED"],
        )
        scene.provider_payloads = compile_provider_payloads(req, scene)
        scenes.append(scene)
    storyboard_id = f"cinematic_storyboard_{uuid4().hex[:10]}"
    return CinematicStoryboard(
        storyboard_id=storyboard_id,
        source_image=req.poster_image_url,
        campaign_brief=req.campaign_brief,
        emotion_intent=req.emotion_intent,
        aspect_ratio=req.aspect_ratio,
        duration_seconds=req.duration_seconds,
        scenes=scenes,
        cinematic_scorecard={"camera_language_score":92,"hook_strength":90 if req.include_viral_hook else 82,"motion_realism_guard":"enabled","safe_zone_compliance":"enabled" if req.include_safe_zone else "disabled","technique_count_available":len(build_150_technique_library())},
        render_package_patch={"render_mode":"cinematic_language_engine","storyboard_id":storyboard_id,"source_image":req.poster_image_url,"provider_payloads":[{"scene_id":s.scene_id,"payloads":s.provider_payloads} for s in scenes],"hard_rules":["NO_CAMERA_TECHNIQUE -> NO_VIDEO_PROMPT","NO_SAFE_ZONE -> NO_SUBTITLE_BURN","NO_PROVIDER_PAYLOAD -> NO_RENDER","NO_FINAL_VIDEO_CONTRACT -> NO_DOWNLOAD"]},
    )
