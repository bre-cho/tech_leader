from __future__ import annotations

import hashlib
import os
import time
from typing import Any



class TTSSynthesisError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        scene_id: str | None = None,
        backend: str = "elevenlabs",
        original_exc: Exception | None = None,
    ) -> None:
        self.scene_id = scene_id
        self.backend = backend
        self.original_exc = original_exc
        super().__init__(message)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (AttributeError, TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except (AttributeError, TypeError, ValueError):
        return default


def _tts_enabled() -> bool:
    return _env_bool("DRAMA_TTS_ENABLED", False)


def _stub_result(text: str, *, scene_id: str | None = None, reason: str = "stub_disabled") -> dict[str, Any]:
    token_source = scene_id or text or "line"
    token = hashlib.sha1(token_source.encode("utf-8")).hexdigest()[:12]
    # Production fake-success enforcement occurs via assert_no_fake_success_payload.
    return {
        "audio_url": f"https://example.invalid/drama-tts-stub-{token}.mp3",
        "duration_seconds": 0.0,
        "backend": "stub",
        "stub": True,
        "reason": reason,
        "scene_id": scene_id,
        "word_timings": [],
    }


def _lookup_voice_id(
    *,
    character_id: str | None,
    voice_id: str | None,
    emotion: str | None,
    language: str | None,
) -> str:
    if voice_id:
        return str(voice_id)
    if character_id:
        return str(character_id)
    if emotion:
        return f"{emotion}-{language or 'en'}"
    return os.getenv("DRAMA_TTS_DEFAULT_VOICE_ID", "default")


def _is_rate_limit_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    message = str(exc).lower()
    return "429" in message or "rate limit" in message


def _retry_sleep_seconds(attempt: int) -> float:
    base = max(0.1, _env_float("DRAMA_TTS_RETRY_BASE_SEC", 1.0))
    max_sleep = max(base, _env_float("DRAMA_TTS_RETRY_MAX_SEC", 8.0))
    return min(max_sleep, base * (2 ** max(0, attempt - 1)))


def _synthesize_elevenlabs(
    text: str,
    *,
    character_id: str | None,
    voice_id: str | None,
    emotion: str | None,
    language: str | None,
    scene_id: str | None,
) -> dict[str, Any]:
    try:
        from app.services.audio.elevenlabs_adapter import ElevenLabsAdapter  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        raise TTSSynthesisError(
            "Failed to import ElevenLabs adapter",
            scene_id=scene_id,
            backend="elevenlabs",
            original_exc=exc,
        ) from exc

    import app.core.async_utils as async_utils_mod  # noqa: PLC0415

    adapter = ElevenLabsAdapter()
    resolved_voice_id = _lookup_voice_id(
        character_id=character_id,
        voice_id=voice_id,
        emotion=emotion,
        language=language,
    )

    retries = max(0, _env_int("DRAMA_TTS_MAX_RETRIES", 2))
    last_exc: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            if hasattr(adapter, "synthesize_text"):
                result = async_utils_mod.run_async(
                    adapter.synthesize_text(
                        voice_id=resolved_voice_id,
                        text=text,
                        emotion=emotion,
                        language=language or "en",
                    )
                )
            else:
                result = async_utils_mod.run_async(
                    adapter.synthesize_speech(
                        voice_id=resolved_voice_id,
                        text=text,
                    )
                )

            if isinstance(result, dict):
                return {
                    "audio_url": result.get("audio_url"),
                    "duration_seconds": float(result.get("duration_seconds") or 0.0),
                    "backend": "elevenlabs",
                    "stub": False,
                    "scene_id": scene_id,
                    "word_timings": result.get("word_timings", []),
                }

            return {
                "audio_url": "",
                "audio_bytes": result,
                "duration_seconds": 0.0,
                "backend": "elevenlabs",
                "stub": False,
                "scene_id": scene_id,
                "word_timings": [],
            }
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if _is_rate_limit_error(exc) and attempt <= retries:
                time.sleep(_retry_sleep_seconds(attempt))
                continue
            raise TTSSynthesisError(
                "ElevenLabs synthesis failed",
                scene_id=scene_id,
                backend="elevenlabs",
                original_exc=exc,
            ) from exc

    raise TTSSynthesisError(
        "ElevenLabs synthesis failed after retries",
        scene_id=scene_id,
        backend="elevenlabs",
        original_exc=last_exc,
    )


def synthesize_line(
    text: str,
    *,
    scene_id: str | None = None,
    character_id: str | None = None,
    voice_id: str | None = None,
    emotion: str | None = None,
    language: str | None = "en",
) -> dict[str, Any]:
    normalized_text = (text or "").strip()
    if not normalized_text:
        return _stub_result(normalized_text, scene_id=scene_id, reason="empty_text")

    if not _tts_enabled():
        return _stub_result(normalized_text, scene_id=scene_id, reason="tts_disabled")

    backend = os.getenv("DRAMA_TTS_BACKEND", "elevenlabs").strip().lower()
    if backend != "elevenlabs":
        return _stub_result(normalized_text, scene_id=scene_id, reason=f"unsupported_backend:{backend or 'unset'}")

    return _synthesize_elevenlabs(
        normalized_text,
        character_id=character_id,
        voice_id=voice_id,
        emotion=emotion,
        language=language,
        scene_id=scene_id,
    )
