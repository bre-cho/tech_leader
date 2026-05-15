from __future__ import annotations

import hashlib
from pathlib import Path

from app.tts_studio.contracts import GenerateLineRequest, GeneratedTake, TTSProvider
from app.tts_studio.scenema_audio_provider import ScenemaAudioProviderBoundary


class IndexTTSProviderBoundary:
    '''
    Provider boundary for IndexTTS2.

    - mock mode writes deterministic text sidecars for CI/dev.
    - indextts2 mode returns a worker payload so a GPU sidecar can execute real IndexTTS2.
    '''

    def generate_line(self, req: GenerateLineRequest, output_dir: str) -> GeneratedTake:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        take_id = "take_" + hashlib.sha256(
            f"{req.project_id}:{req.line.line_id}:{req.line.text}:{req.line.emotion.model_dump()}".encode()
        ).hexdigest()[:12]

        if req.provider == TTSProvider.scenema_audio:
            return ScenemaAudioProviderBoundary().generate_line(req, output_dir)

        if req.provider == TTSProvider.mock:
            out = Path(output_dir) / f"{take_id}.txt"
            out.write_text(
                "MOCK INDEXTTS2 TAKE\n"
                f"speaker={req.character.display_name}\n"
                f"voice={req.voice.source_wav_path}\n"
                f"text={req.line.text}\n"
                f"emotion={req.line.emotion.model_dump()}\n",
                encoding="utf-8",
            )
            audio_path = str(out)
            duration = req.line.duration_hint or max(1.0, len(req.line.text.split()) * 0.35)
            provider = "mock_indextts2"
        else:
            # In production, enqueue this payload to IndexTTS2 worker.
            out = Path(output_dir) / f"{take_id}_worker_payload.json"
            out.write_text(
                req.model_dump_json(indent=2),
                encoding="utf-8",
            )
            audio_path = str(out)
            duration = req.line.duration_hint or max(1.0, len(req.line.text.split()) * 0.35)
            provider = "indextts2_worker_payload"

        return GeneratedTake(
            take_id=take_id,
            line_id=req.line.line_id,
            speaker_id=req.character.character_id,
            audio_path=audio_path,
            duration=round(duration, 3),
            emotion=req.line.emotion.clipped(),
            provider=provider,
            locked=False,
            metadata={
                "speaker_name": req.character.display_name,
                "voice_id": req.voice.voice_id,
                "manual_emotion": req.line.manual_emotion,
            },
        )
