from .schemas import SequentialRenderStep, SequentialRuntimePlan, StoryboardScene


class SequentialCreativeRuntime:
    def build(self, scenes: list[StoryboardScene], provider: str, planned_batch_size: int) -> SequentialRuntimePlan:
        steps: list[SequentialRenderStep] = []

        for scene in scenes:
            steps.append(
                SequentialRenderStep(
                    batch_index=((scene.scene_index - 1) // planned_batch_size) + 1,
                    scene_index=scene.scene_index,
                    status="queued",
                    max_concurrent_render=1,
                    execution_mode="sequential",
                )
            )

        return SequentialRuntimePlan(
            provider=provider,
            planned_batch_size=planned_batch_size,
            max_concurrent_render=1,
            execution_mode="sequential",
            steps=steps,
        )


sequential_creative_runtime = SequentialCreativeRuntime()
