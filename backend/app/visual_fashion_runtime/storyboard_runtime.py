from math import ceil
from .schemas import FashionStoryboardScene, VisualDNA, CharacterContinuityLock, FashionMotionPlan


class FashionStoryboardRuntime:
    def build(
        self,
        brief: str,
        dna: VisualDNA,
        continuity: CharacterContinuityLock,
        motion: FashionMotionPlan,
        target_duration: float,
        provider: str,
    ) -> list[FashionStoryboardScene]:
        recommended_scene_duration = 8 if provider == "veo" else 6 if provider == "seedance" else 5
        scene_count = max(1, ceil(target_duration / recommended_scene_duration))
        scene_duration = round(target_duration / scene_count, 2)

        if "pastel" in dna.archetype:
            titles = [
                "Low-angle fashion stride",
                "Sunglasses beauty close-up",
                "Pastel wall lean",
                "Jacket flare motion",
                "Skirt spin orbit",
                "Low squat commerce pose",
                "Soft glasses glance",
                "Floating fashion tableau",
                "Handbag hero insert",
                "Hair sweep transition",
                "Social-commerce product beat",
                "Final pastel identity frame",
            ]
        else:
            titles = [
                "Quiet luxury kneeling hero",
                "Jewelry macro detail",
                "Over-shoulder handbag glance",
                "Soft perfume portrait",
                "Overhead hair composition",
                "Pearl flatlay orbit",
                "Satin fabric close-up",
                "Champagne reflection beat",
                "Leather handbag hero",
                "Beauty eye contact",
                "Luxury product arrangement",
                "Final quiet luxury identity frame",
            ]

        scenes = []
        for i in range(scene_count):
            index = i + 1
            title = titles[i % len(titles)]
            camera = motion.camera_rhythm[i % len(motion.camera_rhythm)]
            pose = motion.pose_sequence[i % len(motion.pose_sequence)]

            visual_prompt = (
                f"{brief}. Scene {index}: {title}. "
                f"Archetype: {dna.archetype}. Palette: {', '.join(dna.palette)}. "
                f"Lighting: {dna.lighting_language}. Camera: {camera}. Pose: {pose}. "
                f"Hair: {continuity.hair_identity}. Face: {continuity.face_identity}. "
                f"Materials: {', '.join(dna.material_language)}. "
                f"Luxury signals: {', '.join(dna.luxury_signals)}. "
                f"Keep character identity, face, hair, outfit palette, makeup and accessory hierarchy consistent."
            )

            scenes.append(
                FashionStoryboardScene(
                    scene_index=index,
                    title=title,
                    visual_prompt=visual_prompt,
                    camera=camera,
                    motion=pose,
                    duration=scene_duration,
                    provider=provider,
                    continuity_notes=continuity.drift_guards,
                )
            )

        return scenes


fashion_storyboard_runtime = FashionStoryboardRuntime()
