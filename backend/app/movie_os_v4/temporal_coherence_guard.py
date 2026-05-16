from .schemas import StoryboardScene


class TemporalCoherenceGuard:
    def check(self, scenes: list[StoryboardScene]) -> dict:
        issues: list[str] = []

        for scene in scenes:
            if not scene.continuity_hash:
                issues.append(f"Scene {scene.scene_index} missing continuity hash")

            if scene.duration <= 0:
                issues.append(f"Scene {scene.scene_index} invalid duration")

        return {
            "status": "pass" if not issues else "needs_review",
            "issues": issues,
            "rule": "movie timeline must preserve identity, mood, lens language, and scene order",
        }


temporal_coherence_guard = TemporalCoherenceGuard()
