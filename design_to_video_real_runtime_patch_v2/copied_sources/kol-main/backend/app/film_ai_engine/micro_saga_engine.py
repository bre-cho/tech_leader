from __future__ import annotations
from typing import Any, Dict, List
from .schemas import ProjectBible, ShotBlock

class MicroSagaEngine:
    """Converts storyboard scenes into SEQUENCE > BEAT > SHOT blocks."""
    def build_shot_blocks(self, storyboard: Dict[str, Any], bible: ProjectBible) -> List[ShotBlock]:
        selected = storyboard.get("selected_storyboard") or storyboard.get("storyboard_response", {}).get("selected_storyboard") or {}
        scenes = selected.get("scenes") or storyboard.get("scenes") or []
        blocks: List[ShotBlock] = []
        for idx, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                continue
            goal = scene.get("goal") or f"Scene {idx}"
            visual = scene.get("visual") or scene.get("prompt") or goal
            motion = scene.get("motion") or "subtle cinematic movement"
            lighting = scene.get("lighting") or "premium cinematic lighting"
            vo = scene.get("voiceover") or scene.get("narration") or ""
            camera = scene.get("camera") or "medium shot, slow push-in"
            scale = "macro" if any(k in (camera + visual).lower() for k in ["macro", "close", "detail", "texture"]) else "wide" if "wide" in camera.lower() else "medium"
            blocks.append(ShotBlock(
                shot_id=f"SHOT BLOCK {idx}",
                sequence=f"SEQUENCE {idx}: {goal}",
                beat=f"BEAT {idx}.1",
                time_range=scene.get("time_range") or scene.get("time") or "0-3s",
                camera=camera,
                action=f"{visual}. Movement: {motion}. Lighting source/style: {lighting}.",
                sfx=scene.get("sfx") or "subtle foley synced to motion; restrained room tone",
                narrator_vo=vo,
                scale=scale,
                lighting=lighting,
                micro_movement=motion,
            ))
        return blocks
