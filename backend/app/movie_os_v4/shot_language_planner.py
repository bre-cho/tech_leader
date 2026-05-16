from math import ceil
from .schemas import MoodColorLensProfile, ShotPlanItem


class ShotLanguagePlannerV4:
    def plan(self, duration: float, provider: str, mood: MoodColorLensProfile) -> list[ShotPlanItem]:
        recommended = 8 if provider == "veo" else 6 if provider == "seedance" else 5
        scene_count = max(1, ceil(duration / recommended))
        scene_duration = round(duration / scene_count, 2)

        titles = [
            "First Frame Hook",
            "Hero Identity Reveal",
            "World Establishing Shot",
            "Texture Detail Insert",
            "Emotional Close-up",
            "Transformation Escalation",
            "Power Motion Scene",
            "Emotional Peak",
            "Final Hero Tableau",
        ]

        shot_roles = [
            "hook",
            "identity",
            "worldbuilding",
            "detail",
            "emotion",
            "transformation",
            "motion",
            "peak",
            "payoff",
        ]

        camera_moves = [
            "slow cinematic push-in",
            "controlled portrait glide",
            "wide crane reveal",
            "macro beauty detail",
            "handheld emotional drift",
            "orbit transformation move",
            "dolly with fabric motion",
            "rising hero orbit",
            "final locked tableau",
        ]

        framings = [
            "close-up",
            "medium close-up",
            "wide shot",
            "macro insert",
            "intimate portrait",
            "full body transformation",
            "three-quarter fashion frame",
            "hero wide frame",
            "centered final composition",
        ]

        emotions = [
            "immediate curiosity",
            "identity recognition",
            "world immersion",
            "desire through texture",
            "emotional intimacy",
            "awe escalation",
            "power and movement",
            "peak wonder",
            "final memory imprint",
        ]

        output: list[ShotPlanItem] = []
        for i in range(scene_count):
            output.append(
                ShotPlanItem(
                    scene_index=i + 1,
                    title=titles[i % len(titles)],
                    shot_role=shot_roles[i % len(shot_roles)],
                    camera_move=camera_moves[i % len(camera_moves)],
                    lens=mood.lens,
                    framing=framings[i % len(framings)],
                    motion=camera_moves[i % len(camera_moves)],
                    emotion=emotions[i % len(emotions)],
                    duration=scene_duration,
                    provider=provider,
                )
            )

        return output


shot_language_planner_v4 = ShotLanguagePlannerV4()
