from __future__ import annotations

import uuid

from app.tts_studio.contracts import (
    Timeline,
    TimelineBuildRequest,
    TimelineClip,
    TrackType,
)


class TimelineBuilder:
    '''
    Embedded timeline:
    dialogue, SFX, ambience, music are separate tracks.
    SFX/ambience/music can overlap spoken lines.
    '''

    def build(self, req: TimelineBuildRequest) -> Timeline:
        clips: list[TimelineClip] = []
        t = 0.0

        take_by_line = {t.line_id: t for t in req.takes}
        for line in req.project.lines:
            take = take_by_line.get(line.line_id)
            if not take:
                continue
            start = line.start_hint if line.start_hint is not None else t
            end = start + take.duration
            clips.append(
                TimelineClip(
                    clip_id="clip_" + uuid.uuid4().hex[:10],
                    track_type=TrackType.dialogue,
                    source_id=take.take_id,
                    start=round(start, 3),
                    end=round(end, 3),
                    volume=1.0,
                    locked=line.locked,
                    metadata={"line_id": line.line_id, "speaker_id": line.speaker_id, "audio_path": take.audio_path},
                )
            )
            t = max(t, end + req.crossfade_ms / 1000.0)

        for marker in req.project.sound_markers:
            clips.append(
                TimelineClip(
                    clip_id="clip_" + uuid.uuid4().hex[:10],
                    track_type=marker.type,
                    source_id=marker.marker_id,
                    start=marker.start,
                    end=round(marker.start + marker.duration, 3),
                    volume=marker.volume,
                    locked=False,
                    metadata={"prompt": marker.prompt},
                )
            )

        duration = max([c.end for c in clips], default=0.0)
        return Timeline(
            timeline_id="timeline_" + uuid.uuid4().hex[:10],
            project_id=req.project.project_id,
            clips=sorted(clips, key=lambda c: (c.start, c.track_type.value)),
            duration=round(duration, 3),
            metadata={"tracks": ["dialogue", "sfx", "ambience", "music"]},
        )
