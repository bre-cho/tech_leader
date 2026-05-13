from __future__ import annotations

import re
import uuid
from typing import List

from app.tts_studio.contracts import (
    CharacterProfile,
    EmotionVector,
    ScriptCanvasProject,
    ScriptLine,
    SoundMarker,
    TrackType,
)
from app.tts_studio.emotion_engine import EmotionVectorEngine


MARKER_RE = re.compile(r"\[\[(SFX|AMBIENCE|MUSIC):\s*(.*?)(?:\|\s*duration=(\d+(?:\.\d+)?))?\]\]", re.I)


class ScriptCanvasParser:
    '''
    Converts a script into dialogue lines and sound sidecar markers.

    Supports Draft-to-Take style markers:
    [[SFX: iron gate latch lifting | duration=2.2]]
    [[AMBIENCE: soft spa room tone]]
    [[MUSIC: premium beauty pulse | duration=24]]
    '''

    def __init__(self):
        self.emotion_engine = EmotionVectorEngine()

    def parse(self, title: str, script: str, default_speaker_id: str = "char_narrator") -> ScriptCanvasProject:
        project_id = "proj_" + uuid.uuid4().hex[:12]
        lines: List[ScriptLine] = []
        markers: List[SoundMarker] = []

        current_time = 0.0
        for raw in [x.strip() for x in script.splitlines() if x.strip()]:
            marker = MARKER_RE.search(raw)
            if marker:
                typ = marker.group(1).lower()
                prompt = marker.group(2).strip()
                duration = float(marker.group(3) or 2.0)
                markers.append(
                    SoundMarker(
                        marker_id="mk_" + uuid.uuid4().hex[:10],
                        type=TrackType(typ.lower() if typ.lower() != "ambience" else "ambience"),
                        prompt=prompt,
                        start=current_time,
                        duration=duration,
                        volume=0.35 if typ.lower() in ["ambience", "music"] else 0.65,
                    )
                )
                if typ.lower() != "ambience":
                    current_time += min(duration, 3.0)
                continue

            speaker_id = default_speaker_id
            text = raw
            if ":" in raw and len(raw.split(":", 1)[0]) <= 32:
                speaker, text = raw.split(":", 1)
                speaker_id = "char_" + re.sub(r"\W+", "_", speaker.strip().lower()).strip("_")
                text = text.strip()

            duration_hint = max(1.2, len(text.split()) * 0.35)
            emotion = self.emotion_engine.detect(text)
            lines.append(
                ScriptLine(
                    line_id="line_" + uuid.uuid4().hex[:10],
                    speaker_id=speaker_id,
                    text=text,
                    start_hint=current_time,
                    duration_hint=round(duration_hint, 2),
                    emotion=emotion,
                    manual_emotion=False,
                )
            )
            current_time += duration_hint

        return ScriptCanvasProject(
            project_id=project_id,
            title=title,
            lines=lines,
            sound_markers=markers,
            metadata={"parser": "IndexTTSWorkflowStudioInspiredScriptCanvas"},
        )
