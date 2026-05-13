from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from app.video_postprocess.ffmpeg_utils import ensure_file, get_duration, run_cmd


class RealAudioMixService:
    '''
    Production audio mix copied/adapted from kol-main-4 render_production flow.

    Role in MVP:
    - runs after TTS/narration is ready
    - before subtitle burn/mux
    - outputs normalized AAC track for final video assembly

    Features:
    - voice first
    - optional BGM looped to voice duration
    - sidechain compression for BGM under voice
    - optional SFX tracks
    - loudnorm to target LUFS
    '''

    def mix(
        self,
        *,
        voice_path: str,
        output_path: str,
        bgm_path: Optional[str] = None,
        sfx_paths: Optional[Iterable[str]] = None,
        target_lufs: float = -14.0,
        bgm_volume: float = 0.18,
        sfx_volume: float = 0.55,
    ) -> str:
        voice = ensure_file(voice_path, "voice audio")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        inputs: List[str] = [str(voice)]
        if bgm_path:
            inputs.append(str(ensure_file(bgm_path, "background music")))
        for p in sfx_paths or []:
            inputs.append(str(ensure_file(p, "sound effect")))

        cmd = ["ffmpeg", "-y"]
        for p in inputs:
            cmd += ["-i", p]

        if len(inputs) == 1:
            filter_complex = f"[0:a]loudnorm=I={target_lufs}:TP=-1.5:LRA=11[aout]"
        else:
            chains = ["[0:a]volume=1.0[a0]"]
            amix_inputs = ["[a0]"]
            idx = 1

            if bgm_path:
                voice_duration = max(get_duration(voice), 1.0)
                chains.append(
                    f"[{idx}:a]aloop=loop=-1:size=2e+09,"
                    f"atrim=0:{voice_duration:.3f},"
                    f"volume={bgm_volume},"
                    f"sidechaincompress=threshold=0.025:ratio=8:attack=80:release=700[bgm]"
                )
                amix_inputs.append("[bgm]")
                idx += 1

            for n, _ in enumerate(sfx_paths or []):
                chains.append(f"[{idx}:a]volume={sfx_volume}[sfx{n}]")
                amix_inputs.append(f"[sfx{n}]")
                idx += 1

            filter_complex = (
                ";".join(chains)
                + ";"
                + "".join(amix_inputs)
                + f"amix=inputs={len(amix_inputs)}:duration=first:dropout_transition=0,"
                + f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11[aout]"
            )

        cmd += [
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path,
        ]
        run_cmd(cmd, label="audio mix")
        ensure_file(output_path, "mixed audio")
        return output_path
