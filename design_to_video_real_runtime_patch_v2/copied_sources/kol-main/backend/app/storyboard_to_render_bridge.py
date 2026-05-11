"""Poster/Campaign Brief -> Storyboard -> Provider render payload bridge.

This additive bridge connects AUTO_STORYBOARD_ENGINE_V2 with the extracted render,
provider, avatar, drama, audio, audio-mix, and voice-clone modules copied from
brain-main(10).zip. It is intentionally dependency-light so it can run even while
legacy provider modules are being wired into a larger FastAPI/Celery app.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.storyboard_engine.service import AutoStoryboardService
from app.storyboard_engine.schemas import PosterInput
from app.smart_subtitle_engine.schemas import SmartSubtitleRequest, PlatformPreset, SubtitleIntensity
from app.smart_subtitle_engine.service import SmartSubtitleService

try:
    from app.film_ai_engine.film_ai_orchestrator import FilmAIOrchestrator
except Exception:  # keep bridge dependency-light during partial merges
    FilmAIOrchestrator = None


SUPPORTED_PROVIDERS = {"veo", "runway", "kling", "seedance", "seedance2", "volcengine"}


@dataclass(frozen=True)
class RenderHandoffOptions:
    providers: List[str]
    aspect_ratio: str = "9:16"
    render_mode: str = "text_to_video"
    include_audio: bool = True
    include_avatar: bool = True
    include_drama: bool = True
    include_voice_clone: bool = False
    enable_film_ai_upgrade: bool = True
    include_karaoke_subtitle: bool = True
    include_smart_subtitle: bool = True


class StoryboardToRenderBridge:
    """Compiles storyboard scenes into render-ready multi-provider payloads."""

    def __init__(self, storyboard_service: Optional[AutoStoryboardService] = None):
        self.storyboard_service = storyboard_service or AutoStoryboardService()

    def build_render_package(
        self,
        request: PosterInput,
        options: Optional[RenderHandoffOptions] = None,
    ) -> Dict[str, Any]:
        options = options or RenderHandoffOptions(providers=["veo", "runway", "kling", "seedance2"])
        providers = [p.lower() for p in options.providers if p.lower() in SUPPORTED_PROVIDERS]
        if not providers:
            raise ValueError("At least one supported provider is required")

        storyboard_model = self.storyboard_service.run(request)
        storyboard = storyboard_model.model_dump(mode="json")
        selected = next((s for s in storyboard.get("storyboards", []) if s.get("variant") == storyboard.get("recommended_variant")), storyboard.get("storyboards", [{}])[0] if storyboard.get("storyboards") else {})
        scenes = selected.get("scenes", [])

        provider_payloads: List[Dict[str, Any]] = []
        for scene in scenes:
            scene_dict = scene if isinstance(scene, dict) else scene.model_dump()
            prompt = scene_dict.get("video_prompt") or scene_dict.get("prompt") or scene_dict.get("visual", "")
            for provider in providers:
                provider_payloads.append(self._compile_provider_payload(provider, scene_dict, prompt, options))

        package = {
            "pipeline": "poster_to_storyboard_to_render_v1",
            "hard_rules": [
                "NO_POSTER_ANALYSIS_NO_STORYBOARD",
                "NO_SELLING_MECHANISM_NO_SCRIPT",
                "NO_CAMERA_RULE_NO_VIDEO_PROMPT",
                "NO_SCENE_JSON_NO_RENDER",
                "NO_PROVIDER_EXPORT_NO_PRODUCTION",
            ],
            "storyboard_response": storyboard,
            "selected_storyboard": selected,
            "render_handoff": {
                "providers": providers,
                "aspect_ratio": options.aspect_ratio,
                "render_mode": options.render_mode,
                "scene_count": len(scenes),
                "payload_count": len(provider_payloads),
                "payloads": provider_payloads,
            },
            "audio_plan": self._build_audio_plan(storyboard, options),
            "avatar_plan": self._build_avatar_plan(storyboard, options),
            "drama_plan": self._build_drama_plan(storyboard, options),
            "karaoke_subtitle_plan": self._build_karaoke_subtitle_plan(storyboard, selected, options),
            "smart_subtitle_plan": self._build_smart_subtitle_plan(storyboard, selected, options),
        }
        if options.enable_film_ai_upgrade and FilmAIOrchestrator is not None:
            try:
                brief = request.campaign_brief.model_dump(mode="json") if hasattr(request.campaign_brief, "model_dump") else {}
                return FilmAIOrchestrator().upgrade_render_package(package, campaign_brief=brief, poster_analysis=storyboard.get("poster_analysis"), providers=providers)
            except Exception as exc:
                package["film_ai_upgrade_error"] = str(exc)
        return package

    def _compile_provider_payload(
        self,
        provider: str,
        scene: Dict[str, Any],
        prompt: str,
        options: RenderHandoffOptions,
    ) -> Dict[str, Any]:
        duration = self._scene_duration_seconds(scene.get("time_range", "0-3s"))
        common = {
            "provider": provider,
            "scene_id": scene.get("scene_id"),
            "duration": duration,
            "aspect_ratio": options.aspect_ratio,
            "mode": options.render_mode,
            "prompt": prompt,
            "negative_prompt": "watermark, distorted text, plastic skin, exaggerated anatomy, cropped subject, unsafe framing",
            "camera": scene.get("camera"),
            "motion": scene.get("motion"),
            "lighting": scene.get("lighting"),
            "voiceover": scene.get("voiceover"),
            "on_screen_text": scene.get("on_screen_text"),
        }
        if provider == "runway":
            return {**common, "model": "gen4_turbo", "runway": {"ratio": options.aspect_ratio}}
        if provider == "kling":
            return {**common, "kling": {"cfg_scale": 0.5, "camera_control": scene.get("camera")}}
        if provider in {"seedance", "seedance2", "volcengine"}:
            return {**common, "seedance": {"resolution": "1080p", "prompt_optimizer": True}}
        if provider == "veo":
            return {**common, "veo": {"safety_margin": "mobile_safe", "generate_audio": False}}
        return common

    def _build_audio_plan(self, storyboard: Dict[str, Any], options: RenderHandoffOptions) -> Dict[str, Any]:
        if not options.include_audio:
            return {"enabled": False}
        scenes = storyboard.get("scenes", []) if isinstance(storyboard, dict) else []
        return {
            "enabled": True,
            "modules": ["narration_service", "audio_mix_service", "audio_mux_service", "breath_pacing_service"],
            "voice_clone_enabled": options.include_voice_clone,
            "tracks": [
                {"scene_id": s.get("scene_id"), "voiceover": s.get("voiceover"), "mix_role": "narration"}
                for s in scenes if isinstance(s, dict)
            ],
        }

    def _build_avatar_plan(self, storyboard: Dict[str, Any], options: RenderHandoffOptions) -> Dict[str, Any]:
        return {
            "enabled": options.include_avatar,
            "modules": ["avatar_identity_engine", "avatar_continuity_engine", "avatar_scene_mapper", "render_quality_gate"],
            "continuity_policy": "lock_identity_across_scenes",
        }


    def _build_karaoke_subtitle_plan(self, storyboard: Dict[str, Any], selected: Dict[str, Any], options: RenderHandoffOptions) -> Dict[str, Any]:
        if not options.include_karaoke_subtitle:
            return {"enabled": False}
        scenes = selected.get("scenes", []) if isinstance(selected, dict) else []
        return {
            "enabled": True,
            "modules": [
                "render.assembly.subtitles.word_level_karaoke_writer",
                "render.assembly.subtitles.visual_aware_karaoke_writer",
                "render.assembly.vision.subtitle_safe_zone_engine",
                "media.subtitle_burner",
            ],
            "format": "ASS karaoke + optional SRT sidecar",
            "timing_source_priority": ["tts_word_timestamps", "asr_alignment", "estimated_scene_timing"],
            "lines": [
                {"scene_id": s.get("scene_id"), "time_range": s.get("time_range") or s.get("time"), "text": s.get("voiceover") or s.get("on_screen_text")}
                for s in scenes if isinstance(s, dict)
            ],
            "hard_rules": ["NO_VOICE_NO_SUBTITLE", "NO_SUBTITLE_NO_KARAOKE", "NO_SAFE_ZONE_NO_BURN_IN"],
        }


    def _build_smart_subtitle_plan(self, storyboard: Dict[str, Any], selected: Dict[str, Any], options: RenderHandoffOptions) -> Dict[str, Any]:
        if not options.include_smart_subtitle:
            return {"enabled": False}
        scenes = selected.get("scenes", []) if isinstance(selected, dict) else []
        service = SmartSubtitleService()
        packages: List[Dict[str, Any]] = []
        platform = PlatformPreset.tiktok if options.aspect_ratio == "9:16" else PlatformPreset.youtube_16x9
        for s in scenes:
            if not isinstance(s, dict):
                continue
            script = s.get("voiceover") or s.get("on_screen_text") or s.get("visual") or ""
            if not script:
                continue
            duration = self._scene_duration_seconds(s.get("time_range") or s.get("time") or "0-3s")
            emotion = self._infer_subtitle_emotion(s)
            response = service.build(
                SmartSubtitleRequest(
                    script=script,
                    duration=float(duration),
                    platform=platform,
                    aspect_ratio=options.aspect_ratio,
                    scene_id=str(s.get("scene_id") or "scene"),
                    scene_emotion=emotion,
                    metadata={"source": "storyboard_to_render_bridge", "camera": s.get("camera"), "lighting": s.get("lighting")},
                )
            )
            data = response.model_dump(mode="json")
            # Keep payload compact: full ASS/SRT are exposed by /api/subtitles/smart-package when needed.
            data["ass_preview"] = data.pop("ass_text")[:1200]
            data["srt_preview"] = data.pop("srt_text")[:800]
            packages.append(data)
        return {
            "enabled": True,
            "engine": "P17_SMART_SUBTITLE_ENGINE",
            "modules": [
                "smart_subtitle_engine.timing_engine",
                "smart_subtitle_engine.style_engine",
                "smart_subtitle_engine.safe_zone_engine",
                "smart_subtitle_engine.ui_detector",
                "smart_subtitle_engine.ass_writer",
            ],
            "features": ["auto_style", "word_level_karaoke", "platform_safe_zone", "yolo_detect_ui_avoidance", "ass_srt_export"],
            "packages": packages,
            "hard_rules": ["NO_VOICE_NO_SUBTITLE", "NO_SAFE_ZONE_NO_BURN_IN", "NO_STYLE_NO_EXPORT", "NO_KARAOKE_TIMING_NO_ASS"],
        }

    @staticmethod
    def _infer_subtitle_emotion(scene: Dict[str, Any]) -> SubtitleIntensity:
        text = " ".join(str(scene.get(k, "")) for k in ("goal", "visual", "lighting", "motion", "video_prompt")).lower()
        if any(k in text for k in ["asmr", "silence", "whisper", "meditative", "slow"]):
            return SubtitleIntensity.asmr
        if any(k in text for k in ["shock", "viral", "bold", "attention", "hook"]):
            return SubtitleIntensity.viral
        if any(k in text for k in ["dramatic", "tension", "climax", "conflict"]):
            return SubtitleIntensity.dramatic
        if any(k in text for k in ["documentary", "history", "narrative", "saga"]):
            return SubtitleIntensity.documentary
        return SubtitleIntensity.luxury

    def _build_drama_plan(self, storyboard: Dict[str, Any], options: RenderHandoffOptions) -> Dict[str, Any]:
        return {
            "enabled": options.include_drama,
            "modules": ["tension_engine", "camera_drama_engine", "continuity_engine", "drama_veo_prompt_translator"],
            "role": "raise hook, tension, transformation, and final brand close",
        }

    @staticmethod
    def _scene_duration_seconds(time_label: str) -> int:
        try:
            raw = time_label.replace("s", "")
            start, end = raw.split("-")
            return max(1, int(float(end) - float(start)))
        except Exception:
            return 3
