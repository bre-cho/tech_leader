from __future__ import annotations
from .schemas import ShotTechnique

def build_150_technique_library() -> list[ShotTechnique]:
    base = [
        ("low_angle_hero","hero_power","Low Angle Hero","low wide shot","24mm","slow rise push-in","power dominance confidence",["product","fashion","car"],"foreground dominance, towering perspective, premium hero lighting"),
        ("extreme_macro_texture","detail","Extreme Macro Texture","extreme close-up","100mm macro","rack focus micro slide","premium tactility proof",["beauty","food","luxury","car"],"macro texture, condensation, reflections, material detail"),
        ("orbit_180_product","motion_showcase","180 Product Orbit","wide hero","35mm anamorphic","smooth 180 degree orbit","dimension and premium reveal",["product","car","fashion"],"smooth orbit, parallax reflections, stable identity"),
        ("whip_pan_transition","viral_energy","Whip Pan Transition","medium kinetic","35mm","fast whip pan","viral kinetic energy",["ugc","news","commerce"],"controlled whip pan, motion blur, impact cut"),
        ("crash_zoom_hook","viral_energy","Crash Zoom Hook","medium close","35mm","fast crash zoom","scroll stop urgency",["tiktok","news","commerce"],"fast push zoom in first 0.5 seconds"),
        ("slow_luxury_dolly","luxury","Slow Luxury Dolly","medium wide","50mm","slow dolly-in","premium calm desire",["luxury","fashion","perfume"],"smooth dolly, shallow depth of field, soft highlight"),
        ("floating_gimbal","luxury","Floating Gimbal","wide contextual","35mm","floating gimbal drift","elegant dreamlike motion",["fashion","beauty","real_estate"],"floating camera, slow parallax, calm luxury"),
        ("handheld_tension","tension","Handheld Tension","tight medium","35mm","subtle handheld micro-shake","urgency realism",["drama","news","documentary"],"subtle shake, compressed framing, high tension"),
        ("top_down_graphic","motion_design","Top Down Graphic","top-down","35mm","vertical crane down","clarity and structure",["finance","tech","food"],"top-down layout, clean motion graphic composition"),
        ("rack_focus_reveal","reveal","Rack Focus Reveal","close-up","85mm","rack focus foreground to subject","curiosity reveal",["product","beauty","story"],"foreground blur resolving into hero subject"),
        ("silhouette_backlight","mystery","Silhouette Backlight","wide silhouette","50mm","slow push-in","mystery premium drama",["fashion","car","cinematic"],"strong backlight, silhouette shape, volumetric haze"),
        ("pov_immersion","immersion","POV Immersion","POV","24mm","natural handheld follow","first-person involvement",["travel","food","ugc"],"POV motion, natural perspective, immersive action"),
        ("dutch_angle_disrupt","tension","Dutch Angle Disruption","dutch angle medium","35mm","slow tilted push","unease disruption",["drama","shock","news"],"slight dutch angle, visual instability"),
        ("drone_establish","scale","Drone Establishing","aerial wide","24mm","drone push forward","scale and authority",["car","real_estate","travel"],"aerial reveal, large environment, cinematic scale"),
        ("profile_tracking","fashion","Profile Tracking","side profile","70mm","lateral tracking","elegant movement",["fashion","car","lifestyle"],"profile tracking, clean silhouette, parallel motion"),
        ("insert_cutaway","editorial","Insert Cutaway","insert shot","85mm","static or micro push","proof and clarity",["ads","education","commerce"],"insert detail, evidence, quick editorial cutaway"),
        ("split_reveal","transformation","Split Reveal","medium split","50mm","wipe reveal","before-after transformation",["beauty","fitness","product"],"split reveal, transformation contrast"),
        ("speed_ramp_reveal","viral_energy","Speed Ramp Reveal","wide to close","35mm","speed ramp push","impact and retention",["sports","commerce","car"],"fast-to-slow ramp, impact moment"),
        ("parallax_depth_push","cinematic","Parallax Depth Push","layered wide","35mm","slow push through foreground","depth and richness",["luxury","story","product"],"foreground elements, background parallax, depth"),
        ("cta_static_lockup","conversion","CTA Static Lockup","clean medium","50mm","static premium frame","trust close and conversion",["ads","ecommerce"],"stable final frame, CTA safe zone, brand lockup"),
    ]
    techniques = []
    for item in base:
        tid, fam, name, shot, lens, motion, effect, best, fragment = item
        techniques.append(ShotTechnique(
            technique_id=tid, family=fam, name=name, shot_type=shot, lens=lens,
            camera_motion=motion, emotional_effect=effect, best_for=best,
            provider_notes={
                "veo": "Stable cinematic motion; avoid rapid identity-breaking moves.",
                "runway": "Strong for fashion/beauty and controlled motion.",
                "kling": "Good for expressive commercial motion.",
                "seedance2": "Prioritize 2-second hook and kinetic camera grammar.",
                "html_motion": "Use deterministic typography/product motion fallback.",
            },
            prompt_fragment=fragment,
        ))
    families = ["hook","detail","trust","luxury","power","freshness","mystery","authority","ugc","commerce","beauty","fashion","auto"]
    motions = ["slow push-in","micro dolly","lateral slide","subtle orbit","tilt reveal","crane down","dolly out","whip micro-pan"]
    lenses = ["24mm","35mm","50mm","85mm","100mm macro"]
    idx = 1
    for fam in families:
        for motion in motions:
            for lens in lenses:
                if len(techniques) >= 150:
                    return techniques
                techniques.append(ShotTechnique(
                    technique_id=f"{fam}_{motion.replace(' ','_').replace('-','_')}_{lens.replace('mm','').replace(' ','_')}_{idx}",
                    family=fam,
                    name=f"{fam.title()} {motion.title()} {lens}",
                    shot_type="cinematic commercial shot",
                    lens=lens,
                    camera_motion=motion,
                    emotional_effect=f"{fam} visual psychology",
                    best_for=["product","short_video","ads"],
                    provider_notes={"seedance2": "Strong in first two seconds.", "veo": "Keep motion controlled."},
                    prompt_fragment=f"{fam} commercial composition, {motion}, {lens}, premium light, safe framing",
                ))
                idx += 1
    return techniques
