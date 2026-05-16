class SafeSequentialRenderQueue:
    def build_execution_steps(self, scene_count: int, planned_batch_size: int):
        steps = []
        for scene_index in range(1, scene_count + 1):
            steps.append({
                "batch_index": ((scene_index - 1) // planned_batch_size) + 1,
                "scene_index": scene_index,
                "status": "queued",
                "max_concurrent_render": 1,
                "execution_mode": "sequential",
            })
        return steps

safe_render_queue = SafeSequentialRenderQueue()
