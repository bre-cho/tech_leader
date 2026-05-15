from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional
from xml.sax.saxutils import escape

from app.tts_studio.contracts import GenerateLineRequest, GeneratedTake


class ScenemaAudioError(RuntimeError):
    pass


class ScenemaAudioProviderBoundary:
    """HTTP provider boundary for Scenema Audio sidecar.

    Scenema Audio runs as a separate GPU service and exposes POST /generate.
    This boundary keeps the main Tech Leader backend lightweight and CI-safe:
    when SCENEMA_AUDIO_DRY_RUN=true it writes the exact worker payload instead
    of calling the GPU sidecar.
    """

    def __init__(self, api_url: Optional[str] = None, dry_run: Optional[bool] = None, timeout_s: Optional[int] = None):
        self.api_url = (api_url or os.getenv("SCENEMA_AUDIO_URL", "http://localhost:8000")).rstrip("/")
        self.dry_run = self._as_bool(os.getenv("SCENEMA_AUDIO_DRY_RUN", "false")) if dry_run is None else dry_run
        self.timeout_s = int(timeout_s or os.getenv("SCENEMA_AUDIO_TIMEOUT_S", "900"))

    @staticmethod
    def _as_bool(value: str) -> bool:
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def generate_line(self, req: GenerateLineRequest, output_dir: str) -> GeneratedTake:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        take_id = "take_" + hashlib.sha256(
            f"scenema:{req.project_id}:{req.line.line_id}:{req.line.text}:{req.line.emotion.model_dump()}:{req.voice.voice_id}".encode()
        ).hexdigest()[:12]

        prompt = self.build_prompt(req)
        payload = self.build_payload(req, prompt)

        if self.dry_run:
            out = Path(output_dir) / f"{take_id}_scenema_payload.json"
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            audio_path = str(out)
            duration = self.estimate_duration(req)
            provider = "scenema_audio_payload"
            metadata: Dict[str, Any] = {"dry_run": True, "scenema_url": self.api_url}
        else:
            result = self._call_generate(payload)
            wav = base64.b64decode(result["audio"])
            out = Path(output_dir) / f"{take_id}.wav"
            out.write_bytes(wav)
            meta = result.get("metadata", {})
            audio_path = str(out)
            duration = float(meta.get("duration_s") or self.estimate_duration(req))
            provider = "scenema_audio"
            metadata = {
                "dry_run": False,
                "scenema_url": self.api_url,
                "content_type": result.get("content_type", "audio/wav"),
                "scenema_metadata": meta,
            }

        metadata.update(
            {
                "speaker_name": req.character.display_name,
                "voice_id": req.voice.voice_id,
                "manual_emotion": req.line.manual_emotion,
                "prompt_xml": prompt,
                "mode": payload.get("mode"),
                "language": req.voice.language,
                "reference_voice_url": payload.get("reference_voice_url"),
            }
        )

        return GeneratedTake(
            take_id=take_id,
            line_id=req.line.line_id,
            speaker_id=req.character.character_id,
            audio_path=audio_path,
            duration=round(duration, 3),
            emotion=req.line.emotion.clipped(),
            provider=provider,
            locked=False,
            metadata=metadata,
        )

    def build_prompt(self, req: GenerateLineRequest) -> str:
        voice_desc = req.character.speaking_style or req.voice.metadata.get("voice_description") or req.voice.display_name
        action = self._emotion_to_action(req)
        scene = req.voice.metadata.get("scene") or req.character.metadata.get("scene") or "clean studio narration"
        language = req.voice.language or "vi"
        gender = req.voice.metadata.get("gender") or self._infer_gender(voice_desc)
        shot = req.voice.metadata.get("shot", "closeup")
        attrs = [
            f'voice="{escape(voice_desc)}"',
            f'gender="{escape(gender)}"',
            f'language="{escape(language)}"',
            f'scene="{escape(scene)}"',
            f'shot="{escape(shot)}"',
        ]
        return f"<speak {' '.join(attrs)}>\n  <action>{escape(action)}</action>\n  {escape(req.line.text.strip())}\n</speak>"

    def build_payload(self, req: GenerateLineRequest, prompt: str) -> Dict[str, Any]:
        meta = req.voice.metadata or {}
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "mode": meta.get("mode", "generate"),
            "seed": int(meta.get("seed", 42)),
            "pace": float(meta.get("pace", 1.0)),
            "background_sfx": bool(meta.get("background_sfx", False)),
            "validate": bool(meta.get("validate", False)),
            "skip_vc": bool(meta.get("skip_vc", False)),
            "vc_steps": int(meta.get("vc_steps", 25)),
            "vc_cfg_rate": float(meta.get("vc_cfg_rate", 0.5)),
        }
        reference = meta.get("reference_voice_url") or meta.get("reference_voice_path") or req.voice.source_wav_path
        # Scenema server accepts reference_voice_url. Use URLs directly; local paths are passed
        # through only when the sidecar can see the same mounted volume.
        if reference and reference not in {"/tmp/demo_voice.wav", ""}:
            payload["reference_voice_url"] = reference
        return payload

    def _call_generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = urllib.request.Request(
            f"{self.api_url}/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                result = json.loads(response.read())
        except urllib.error.URLError as exc:
            raise ScenemaAudioError(f"Cannot reach Scenema Audio at {self.api_url}/generate: {exc}") from exc

        if result.get("status") != "succeeded" or "audio" not in result:
            raise ScenemaAudioError(result.get("error", "Scenema Audio generation failed"))
        return result

    def _emotion_to_action(self, req: GenerateLineRequest) -> str:
        e = req.line.emotion.clipped()
        values = e.model_dump()
        top = max(values, key=values.get)
        style = req.character.speaking_style or "natural, clear, commercial"
        if values[top] <= 0.05:
            return f"Deliver naturally with {style}; controlled breath, clear pacing, studio-quality narration."
        mapping = {
            "joy": "warm, optimistic, lightly smiling",
            "anger": "firm, urgent, intense but still intelligible",
            "sadness": "soft, restrained, emotional with slower breath",
            "fear": "tense, careful, with slight breath pressure",
            "disgust": "dry, skeptical, slightly withdrawn",
            "low_mood": "low energy, reflective, heavy pauses",
            "surprise": "bright, lifted, genuinely surprised",
            "calm": "calm, trustworthy, measured and soothing",
        }
        return f"{mapping.get(top, 'expressive')} delivery; keep {style}; preserve pronunciation and clean timing."

    @staticmethod
    def _infer_gender(voice: str) -> str:
        lower = voice.lower()
        female_terms = {"female", "woman", "girl", "she", "her", "feminine", "actress", "mother", "sister"}
        return "female" if any(term in lower for term in female_terms) else "male"

    @staticmethod
    def estimate_duration(req: GenerateLineRequest) -> float:
        return req.line.duration_hint or max(1.0, len(req.line.text.split()) * 0.36)