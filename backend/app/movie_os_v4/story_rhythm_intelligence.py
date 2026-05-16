from .schemas import EmotionalTimelineGraph


class StoryRhythmIntelligence:
    def analyze(self, timeline: EmotionalTimelineGraph) -> dict:
        peak = max(timeline.points, key=lambda p: p.visual_density)
        average_tension = sum(p.tension for p in timeline.points) / max(1, len(timeline.points))
        average_density = sum(p.visual_density for p in timeline.points) / max(1, len(timeline.points))

        return {
            "peak_scene": str(peak.scene_index),
            "average_tension": f"{average_tension:.1f}",
            "average_visual_density": f"{average_density:.1f}",
            "rhythm_quality": "cinematic_escalation",
            "retention_strategy": "hook early, escalate transformation, hold final payoff",
        }


story_rhythm_intelligence = StoryRhythmIntelligence()
