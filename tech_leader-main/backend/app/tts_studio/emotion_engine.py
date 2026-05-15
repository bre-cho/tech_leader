from __future__ import annotations

import re
from app.tts_studio.contracts import EmotionVector


class EmotionVectorEngine:
    '''
    IndexTTS2 emotion vector rules:
    order: joy, anger, sadness, fear, disgust, low_mood, surprise, calm
    each value capped at 0.5; total vector capped at 1.5.
    Manual emotion vectors must not be overwritten unless explicitly requested.
    '''

    def detect(self, text: str, *, preserve_manual: bool = False, existing: EmotionVector | None = None) -> EmotionVector:
        if preserve_manual and existing is not None:
            return existing.clipped()

        s = text.lower()
        vec = EmotionVector()

        if any(w in s for w in ["wow", "bất ngờ", "ngạc nhiên", "không ngờ", "amazing"]):
            vec.surprise = 0.28
        if any(w in s for w in ["vui", "hạnh phúc", "tự tin", "đẹp", "glow", "thích"]):
            vec.joy = 0.25
        if any(w in s for w in ["nhẹ nhàng", "bình tĩnh", "êm", "spa", "thư giãn"]):
            vec.calm = 0.32
        if any(w in s for w in ["sợ", "lo", "đừng bỏ lỡ", "cẩn thận"]):
            vec.fear = 0.18
        if any(w in s for w in ["buồn", "mệt", "stress", "xỉn màu"]):
            vec.low_mood = 0.22
        if re.search(r"!{2,}|🔥|sale|giảm|hot", s):
            vec.surprise = max(vec.surprise, 0.22)
            vec.joy = max(vec.joy, 0.20)

        return vec.clipped()
