from __future__ import annotations

from .schemas import StoryboardVariant


class CameraMotionEngine:
    def plan(self, variant: StoryboardVariant, scene_index: int, total_scenes: int) -> tuple[str, str]:
        if variant == StoryboardVariant.trust:
            cameras = [
                ("clean close-up, eye-level angle", "slow push-in"),
                ("medium product hero shot", "gentle tilt-down"),
                ("macro detail close-up", "slow lateral slider"),
                ("controlled lifestyle medium shot", "smooth dolly-in"),
                ("static brand lockup frame", "soft fade-in"),
            ]
        elif variant == StoryboardVariant.viral:
            cameras = [
                ("extreme close-up, direct gaze", "fast micro push-in"),
                ("low-angle hero shot", "snap dolly reveal"),
                ("macro texture shot", "whip-pan transition"),
                ("dynamic editorial full-body shot", "orbit move"),
                ("poster-style final frame", "impact freeze frame"),
            ]
        else:
            cameras = [
                ("high-impact close-up", "slow push-in"),
                ("medium product reveal", "tilt-down reveal"),
                ("macro detail proof", "lateral slider"),
                ("identity transformation shot", "slow dolly-in"),
                ("final offer/brand frame", "clean locked frame"),
            ]
        return cameras[min(scene_index, len(cameras) - 1)]
