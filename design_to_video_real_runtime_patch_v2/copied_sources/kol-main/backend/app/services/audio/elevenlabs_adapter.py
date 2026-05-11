from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.core.production_gate import is_production_env


class ElevenLabsConfigurationError(RuntimeError):
    """Raised when a required ElevenLabs configuration is missing."""


class ElevenLabsAdapter:
    base_url = "https://api.elevenlabs.io"

    def __init__(self) -> None:
        self.api_key = settings.elevenlabs_api_key
        if is_production_env() and not self.api_key:
            raise ElevenLabsConfigurationError(
                "ELEVENLABS_API_KEY is required in production. "
                "Set the ELEVENLABS_API_KEY environment variable to enable TTS synthesis."
            )

    def _headers(self) -> dict[str, str]:
        return {
            "xi-api-key": self.api_key or "",
        }

    async def list_voices(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(
                f"{self.base_url}/v1/shared-voices",
                headers=self._headers(),
            )
            if resp.status_code >= 400:
                return {"ok": False, "status_code": resp.status_code, "body": resp.text}
            return {"ok": True, "body": resp.json()}

    async def create_ivc_voice(
        self,
        *,
        name: str,
        files: list[str],
        remove_background_noise: bool = True,
    ) -> dict[str, Any]:
        multipart = []
        for file_path in files:
            p = Path(file_path)
            multipart.append(("files", (p.name, p.read_bytes(), "audio/mpeg")))
        multipart.append(("name", (None, name)))
        multipart.append(("remove_background_noise", (None, "true" if remove_background_noise else "false")))

        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/voices/add",
                headers=self._headers(),
                files=multipart,
            )
            if resp.status_code >= 400:
                return {"ok": False, "status_code": resp.status_code, "body": resp.text}
            return {"ok": True, "body": resp.json()}

    async def synthesize_speech(
        self,
        *,
        voice_id: str,
        text: str,
        model_id: str | None = None,
        output_format: str = "mp3_44100_128",
    ) -> bytes:
        payload = {
            "text": text,
            "model_id": model_id or settings.elevenlabs_tts_model_id,
        }
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/text-to-speech/{voice_id}",
                headers={**self._headers(), "Content-Type": "application/json"},
                params={"output_format": output_format},
                json=payload,
            )
            resp.raise_for_status()
            return resp.content

    async def compose_music(
        self,
        *,
        prompt_text: str | None = None,
        duration_seconds: int = 30,
        force_instrumental: bool = True,
    ) -> bytes:
        """Generate a sound/music clip via the ElevenLabs Sound Generation API.

        Uses the ``/v1/sound-generation`` endpoint.  The ``force_instrumental``
        hint is forwarded as ``prompt_influence`` (0.3 favours prompt; ignored
        when ``False``).
        """
        payload: dict = {
            "text": prompt_text or "ambient background music",
            "duration_seconds": duration_seconds,
            "prompt_influence": 0.3 if force_instrumental else 0.5,
        }
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/sound-generation",
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            return resp.content
