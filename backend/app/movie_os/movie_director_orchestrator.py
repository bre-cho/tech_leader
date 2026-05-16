from math import ceil
from .schemas import MovieDirectorRequest, MovieDirectorResponse, MovieScene


class MovieDirectorOrchestrator:
    def _detect_mood(self, prompt: str) -> dict:
        text = prompt.lower()

        if "gothic" in text or "ruby" in text or "queen" in text:
            return {
                "primary_mood": "gothic_luxury",
                "lighting": "ruby velvet low-key cinematic lighting with gold rim highlights",
                "lens": "85mm portrait lens, shallow depth of field",
                "color_script": ["deep ruby", "black velvet", "antique gold"],
                "camera_movement": ["slow push-in", "macro jewel detail", "royal orbit"],
            }

        if "vogue" in text or "couture" in text or "fashion" in text:
            return {
                "primary_mood": "vogue_fantasy",
                "lighting": "high-fashion editorial spotlight with glossy runway reflections",
                "lens": "50mm fashion editorial lens",
                "color_script": ["violet blue", "emerald green", "silver highlight"],
                "camera_movement": ["crane reveal", "runway dolly", "fabric macro"],
            }

        return {
            "primary_mood": "cinematic_fantasy",
            "lighting": "magical volumetric cinematic light",
            "lens": "35mm fantasy cinema lens",
            "color_script": ["violet", "emerald", "moonlit blue", "soft gold"],
            "camera_movement": ["crane reveal", "orbit", "slow cinematic glide"],
        }

    def direct(self, request: MovieDirectorRequest) -> MovieDirectorResponse:
        mood = self._detect_mood(request.prompt)
        recommended = 8 if request.provider == "veo" else 6 if request.provider == "seedance" else 5
        scene_count = max(1, ceil(request.target_duration / recommended))
        scene_duration = round(request.target_duration / scene_count, 2)

        titles = [
            "Opening Hero Reveal",
            "World Atmosphere",
            "Costume Detail",
            "Emotional Close-up",
            "Transformation Motion",
            "Power Pose",
            "Cinematic Orbit",
            "Final Payoff",
        ]

        character_bible = {
            "face": "same cinematic hero face identity across every scene",
            "costume": "mood-consistent cinematic costume",
            "jewelry": "mood-consistent accessories",
            "hairstyle": "consistent hairstyle silhouette",
            "makeup": "consistent cinematic beauty makeup",
            "continuity_rules": [
                "Maintain face identity",
                "Maintain costume palette",
                "Maintain jewelry and hairstyle",
                "Maintain makeup continuity",
            ],
        }

        scenes = []
        for index in range(scene_count):
            scene_index = index + 1
            camera = mood["camera_movement"][index % len(mood["camera_movement"])]
            title = titles[index % len(titles)]
            scenes.append(
                MovieScene(
                    scene_index=scene_index,
                    title=title,
                    visual_prompt=(
                        f"{request.prompt}. Scene {scene_index}: {title}. "
                        f"Lighting: {mood['lighting']}. Lens: {mood['lens']}. "
                        f"Camera: {camera}. Preserve character continuity."
                    ),
                    camera=camera,
                    motion=camera,
                    lens=mood["lens"],
                    lighting=mood["lighting"],
                    duration=scene_duration,
                    continuity_notes=character_bible["continuity_rules"],
                    provider=request.provider,
                )
            )

        rhythm_points = [
            {
                "scene_index": scene.scene_index,
                "emotional_pacing": "hook" if scene.scene_index == 1 else "escalation" if scene.scene_index < scene_count * 0.75 else "payoff",
                "tension": min(95, 45 + scene.scene_index * 4),
                "visual_energy": min(98, 55 + scene.scene_index * 5),
                "retention_goal": "stop scroll" if scene.scene_index == 1 else "maintain attention",
            }
            for scene in scenes
        ]

        return MovieDirectorResponse(
            prompt=request.prompt,
            mood_profile=mood,
            character_bible=character_bible,
            storyboard=scenes,
            rhythm_timeline={
                "duration": request.target_duration,
                "peak_scene_index": max(1, int(scene_count * 0.72)),
                "rhythm_points": rhythm_points,
            },
            editor_plan={
                "edit_style": "cinematic fantasy editorial montage",
                "transitions": ["magic dissolve", "glow wipe", "motion match cut"],
                "pacing_notes": ["hold key faces", "cut on motion", "build to final reveal"],
                "sound_design": ["cinematic pulse", "sparkle accents", "soft ambience"],
                "subtitle_strategy": "minimal cinematic subtitles in safe zone",
            },
            assembly_plan={
                "timeline_tracks": ["video_scene_track", "subtitle_track", "music_track", "transition_track", "color_grade_track"],
                "final_duration": request.target_duration,
                "artifact_targets": ["final_movie_mp4", "preview_mp4", "thumbnail_jpg", "subtitle_srt", "timeline_manifest_json"],
                "export_profiles": ["vertical_9_16_short", "square_1_1_social", "cinematic_16_9_master"],
            },
            sequential_render_policy={
                "planned_batch_size": request.planned_batch_size,
                "max_concurrent_render": 1,
                "execution_mode": "sequential",
                "provider": request.provider,
            },
        )


movie_director_orchestrator = MovieDirectorOrchestrator()
