from .schemas import FinalMovieAssemblyPlan, StoryboardScene


class FinalMovieAssemblyV4:
    def build(self, scenes: list[StoryboardScene], duration: float) -> FinalMovieAssemblyPlan:
        return FinalMovieAssemblyPlan(
            tracks=[
                "video_scene_track",
                "character_continuity_track",
                "voiceover_track",
                "subtitle_track",
                "music_track",
                "sound_design_track",
                "transition_track",
                "color_grade_track",
                "memory_manifest_track",
            ],
            artifact_targets=[
                "final_movie_mp4",
                "preview_movie_mp4",
                "thumbnail_jpg",
                "subtitle_srt",
                "timeline_manifest_json",
                "provider_job_manifest_json",
                "memory_graph_update_json",
                "scene_dependency_graph_json",
            ],
            export_profiles=[
                "vertical_9_16_short",
                "square_1_1_social",
                "cinematic_16_9_master",
            ],
            final_duration=round(duration, 2),
        )


final_movie_assembly_v4 = FinalMovieAssemblyV4()
