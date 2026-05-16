from .schemas import MovieOSV4Request, MovieOSV4Response, StoryboardScene
from .ai_director_brief import ai_director_brief_builder
from .creative_abstraction_layer import creative_abstraction_layer
from .mood_color_lens_engine import mood_color_lens_engine
from .character_continuity_runtime import character_continuity_runtime
from .shot_language_planner import shot_language_planner_v4
from .emotional_timeline_graph import emotional_timeline_graph_builder
from .scene_dependency_rebuilder import scene_dependency_rebuilder
from .temporal_coherence_guard import temporal_coherence_guard
from .runtime_memory_graph import runtime_memory_graph
from .sequential_creative_runtime import sequential_creative_runtime
from .ai_editor import ai_editor_v4
from .final_movie_assembly import final_movie_assembly_v4


class AutonomousMovieOrchestrator:
    def direct(self, request: MovieOSV4Request) -> MovieOSV4Response:
        director_brief = ai_director_brief_builder.build(request.prompt)
        narrative_graph = creative_abstraction_layer.build_narrative_graph(request.prompt)
        mood_profile = mood_color_lens_engine.detect(request.prompt)
        character_bible = character_continuity_runtime.build(request.prompt, mood_profile)
        shot_plan = shot_language_planner_v4.plan(request.target_duration, request.provider, mood_profile)
        emotional_timeline = emotional_timeline_graph_builder.build(request.target_duration, shot_plan)

        storyboard: list[StoryboardScene] = []
        for shot in shot_plan:
            continuity_hash = f"{mood_profile.mood}:{character_bible.identity_lock}:scene:{shot.scene_index}"
            visual_prompt = (
                f"{request.prompt}. {shot.title}. "
                f"Camera: {shot.camera_move}. Lens: {shot.lens}. Framing: {shot.framing}. "
                f"Lighting: {mood_profile.lighting}. Color script: {', '.join(mood_profile.color_script)}. "
                f"Character identity: {character_bible.identity_lock}. Face: {character_bible.face}. "
                f"Costume: {character_bible.costume}. Jewelry: {character_bible.jewelry}. "
                f"Hairstyle: {character_bible.hairstyle}. Makeup: {character_bible.makeup}. "
                f"Preserve temporal coherence with previous and next scenes."
            )

            storyboard.append(
                StoryboardScene(
                    scene_index=shot.scene_index,
                    title=shot.title,
                    visual_prompt=visual_prompt,
                    negative_prompt="face drift, costume inconsistency, random jewelry, broken continuity, overexposed skin, bad anatomy, text, watermark",
                    camera_move=shot.camera_move,
                    lens=shot.lens,
                    lighting=mood_profile.lighting,
                    color_script=mood_profile.color_script,
                    duration=shot.duration,
                    provider=request.provider,
                    continuity_hash=continuity_hash,
                )
            )

        scene_dependency_graph = scene_dependency_rebuilder.build_graph(storyboard)
        temporal_coherence_guard.check(storyboard)
        sequential_runtime_plan = sequential_creative_runtime.build(
            storyboard,
            request.provider,
            request.planned_batch_size,
        )
        editor_plan = ai_editor_v4.build(mood_profile)
        assembly_plan = final_movie_assembly_v4.build(storyboard, request.target_duration)
        memory_update = runtime_memory_graph.update(
            request.memory_namespace,
            mood_profile,
            character_bible,
            request.provider,
        )

        return MovieOSV4Response(
            prompt=request.prompt,
            director_brief=director_brief,
            narrative_graph=narrative_graph,
            mood_profile=mood_profile,
            character_bible=character_bible,
            shot_plan=shot_plan,
            emotional_timeline=emotional_timeline,
            storyboard=storyboard,
            scene_dependency_graph=scene_dependency_graph,
            sequential_runtime_plan=sequential_runtime_plan,
            editor_plan=editor_plan,
            assembly_plan=assembly_plan,
            memory_update=memory_update,
        )


autonomous_movie_orchestrator = AutonomousMovieOrchestrator()
