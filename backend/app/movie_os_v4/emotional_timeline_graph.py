from .schemas import EmotionalTimelineGraph, EmotionalTimelinePoint, ShotPlanItem


class EmotionalTimelineGraphBuilder:
    def build(self, duration: float, shots: list[ShotPlanItem]) -> EmotionalTimelineGraph:
        points: list[EmotionalTimelinePoint] = []
        total = max(1, len(shots))
        peak_scene = max(1, int(total * 0.72))

        for shot in shots:
            progress = shot.scene_index / total

            if progress < 0.15:
                state = "hook"
                tension = 48
                density = 72
                retention = "stop scroll immediately"
                breath = "short silence before first motion"
            elif progress < 0.45:
                state = "immersion"
                tension = 62
                density = 76
                retention = "build curiosity and world depth"
                breath = "soft breath between reveals"
            elif progress < 0.75:
                state = "escalation"
                tension = 84
                density = 92
                retention = "raise transformation tension"
                breath = "accelerated rhythm with short pauses"
            else:
                state = "payoff"
                tension = 72
                density = 96
                retention = "deliver memorable final frame"
                breath = "long emotional hold after final reveal"

            points.append(
                EmotionalTimelinePoint(
                    scene_index=shot.scene_index,
                    emotional_state=state,
                    tension=tension,
                    visual_density=density,
                    retention_goal=retention,
                    silence_or_breath=breath,
                )
            )

        return EmotionalTimelineGraph(
            total_duration=duration,
            peak_scene_index=peak_scene,
            points=points,
        )


emotional_timeline_graph_builder = EmotionalTimelineGraphBuilder()
