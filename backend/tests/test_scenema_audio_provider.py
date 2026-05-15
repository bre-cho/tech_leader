from pathlib import Path

from app.tts_studio.contracts import (
    CharacterProfile,
    EmotionVector,
    GenerateLineRequest,
    ScriptLine,
    TTSProvider,
    VoiceAsset,
)
from app.tts_studio.scenema_audio_provider import ScenemaAudioProviderBoundary


def test_scenema_audio_provider_dry_run_writes_payload(tmp_path: Path):
    req = GenerateLineRequest(
        project_id="proj_demo",
        provider=TTSProvider.scenema_audio,
        line=ScriptLine(
            line_id="line_1",
            speaker_id="speaker_1",
            text="Xin chao, day la mot cau thoai thu nghiem.",
            emotion=EmotionVector(calm=0.3, joy=0.1),
            manual_emotion=True,
        ),
        character=CharacterProfile(
            character_id="char_1",
            display_name="Narrator",
            voice_id="voice_1",
            speaking_style="Vietnamese female narrator, warm cinematic commercial delivery",
        ),
        voice=VoiceAsset(
            voice_id="voice_1",
            display_name="Demo Voice",
            source_wav_path="https://example.com/reference.wav",
            language="vi",
            metadata={"gender": "female", "scene": "studio booth", "pace": 1.05},
        ),
    )

    take = ScenemaAudioProviderBoundary(api_url="http://scenema.local", dry_run=True).generate_line(
        req, str(tmp_path)
    )

    assert take.provider == "scenema_audio_payload"
    assert take.audio_path.endswith("_scenema_payload.json")
    payload = Path(take.audio_path).read_text(encoding="utf-8")
    assert "<speak" in payload
    assert "language=\\\"vi\\\"" in payload
    assert "reference_voice_url" in payload