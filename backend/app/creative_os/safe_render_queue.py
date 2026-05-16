class SafeSequentialRenderQueue:
    def build_execution_steps(self, plan):
        steps = []
        for batch in plan.batches:
            for scene_index in batch.scene_indexes:
                steps.append(
                    {
                        "batch_index": batch.batch_index,
                        "scene_index": scene_index,
                        "status": "queued",
                        "max_concurrent_render": 1,
                        "execution_mode": "sequential",
                    }
                )
        return steps


safe_render_queue = SafeSequentialRenderQueue()
