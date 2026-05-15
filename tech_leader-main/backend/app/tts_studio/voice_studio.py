from __future__ import annotations

import hashlib
from pathlib import Path

from app.tts_studio.contracts import CharacterProfile, EmotionVector, VoiceAsset


class VoiceStudioService:
    '''
    Voice Studio:
    - prepares reusable voices
    - stores voice assets
    - maps voices into character/cast profiles
    '''

    def prepare_voice(self, display_name: str, source_wav_path: str, language: str = "vi") -> VoiceAsset:
        voice_id = "voice_" + hashlib.sha256(f"{display_name}:{source_wav_path}".encode()).hexdigest()[:12]
        return VoiceAsset(
            voice_id=voice_id,
            display_name=display_name,
            source_wav_path=source_wav_path,
            language=language,
            prepared=True,
            tags=["reusable_voice", language],
            metadata={
                "storage_hint": "shared/audio/speakers",
                "source_exists": Path(source_wav_path).exists(),
            },
        )

    def create_character(self, name: str, voice: VoiceAsset, role: str = "narrator") -> CharacterProfile:
        character_id = "char_" + hashlib.sha256(f"{name}:{voice.voice_id}".encode()).hexdigest()[:12]
        return CharacterProfile(
            character_id=character_id,
            display_name=name,
            voice_id=voice.voice_id,
            role=role,
            default_emotion=EmotionVector(calm=0.18).clipped(),
            speaking_style="natural, expressive, commercial, clear Vietnamese delivery",
        )
