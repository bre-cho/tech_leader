from .schemas import SceneDependency, SceneDependencyGraph, SceneRebuildPlan, SceneRebuildRequest, StoryboardScene


class SceneDependencyRebuilder:
    def build_graph(self, scenes: list[StoryboardScene]) -> SceneDependencyGraph:
        dependencies: list[SceneDependency] = []

        for scene in scenes:
            if scene.scene_index > 1:
                dependencies.append(
                    SceneDependency(
                        source_scene=scene.scene_index - 1,
                        target_scene=scene.scene_index,
                        dependency_type="temporal_continuity",
                        rebuild_policy="rebuild_target_if_previous_changes",
                    )
                )

            if scene.scene_index > 2:
                dependencies.append(
                    SceneDependency(
                        source_scene=1,
                        target_scene=scene.scene_index,
                        dependency_type="character_identity_lock",
                        rebuild_policy="preserve_character_bible",
                    )
                )

        return SceneDependencyGraph(dependencies=dependencies)

    def plan_rebuild(self, request: SceneRebuildRequest, total_scenes: int = 12) -> SceneRebuildPlan:
        if request.dependency_policy == "rebuild_scene_and_following":
            affected = list(range(request.scene_index, total_scenes + 1))
        elif request.dependency_policy == "rebuild_dependency_range":
            affected = list(range(max(1, request.scene_index - 1), min(total_scenes, request.scene_index + 2) + 1))
        else:
            affected = [request.scene_index]

        return SceneRebuildPlan(
            scene_index=request.scene_index,
            reason=request.reason,
            affected_scenes=affected,
            dependency_policy=request.dependency_policy,
            max_concurrent_render=1,
            execution_mode="sequential",
        )


scene_dependency_rebuilder = SceneDependencyRebuilder()
