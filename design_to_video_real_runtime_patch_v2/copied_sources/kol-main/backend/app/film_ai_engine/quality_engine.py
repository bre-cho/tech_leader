from __future__ import annotations
from typing import Any, Dict, List

class FilmAIQualityEngine:
    """AEO-aligned QA gate for cinematic poster-to-video packages."""
    def score(self, package: Dict[str, Any]) -> Dict[str, Any]:
        director = package.get("film_ai_director", {})
        render = package.get("render_handoff", {})
        payloads = render.get("payloads", []) + director.get("video_prompts", [])
        checks = {
            "has_project_bible": bool(package.get("project_bible")),
            "has_shot_blocks": bool(package.get("film_ai_shot_blocks")),
            "has_1to1_keyframes": director.get("verification", {}).get("status") == "PASS",
            "has_provider_payloads": bool(payloads),
            "has_aeo_audio": bool(package.get("aeo_audio_plan")),
            "has_karaoke_contract": bool(package.get("karaoke_subtitle_plan")),
        }
        score = round(sum(1 for v in checks.values() if v) / max(1, len(checks)) * 100)
        return {"score": score, "checks": checks, "decision": "PASS" if score >= 85 else "BLOCK", "hard_rules": [
            "NO_PROJECT_BIBLE_NO_PRODUCTION", "NO_SHOT_BLOCKS_NO_RENDER", "NO_1TO1_IMAGE_VIDEO_PARITY_NO_BATCH", "NO_AEO_PLAN_NO_AUDIO", "NO_KARAOKE_CONTRACT_NO_FINAL_VIDEO"
        ]}
