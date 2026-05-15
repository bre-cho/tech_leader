from __future__ import annotations

import subprocess
from pathlib import Path


class FFmpegError(RuntimeError):
    pass


def run_cmd(cmd: list[str], label: str, timeout: int = 900) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise FFmpegError(
            f"{label} failed with code {result.returncode}\n"
            f"cmd={' '.join(cmd)}\nstdout={result.stdout[-2000:]}\nstderr={result.stderr[-4000:]}"
        )
    return result


def assert_media(path: str | Path, label: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{label} missing: {p}")
    if p.stat().st_size <= 0:
        raise ValueError(f"{label} empty: {p}")
    return p


def probe_duration(path: str | Path) -> float:
    assert_media(path, "media")
    r = run_cmd([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ], "ffprobe duration", 60)
    try:
        return float(r.stdout.strip() or "0")
    except ValueError:
        return 0.0


def convert_wav_mono_24k(input_path: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    run_cmd([
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "24000",
        "-af", "loudnorm=I=-20:TP=-2:LRA=11,highpass=f=70,lowpass=f=12000",
        output_path
    ], "voice reference preprocess")
    assert_media(output_path, "preprocessed wav")
    return output_path


def normalize_output_wav(input_path: str, output_path: str, target_lufs: float = -16.0) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    run_cmd([
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "24000",
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
        output_path
    ], "normalize generated wav")
    assert_media(output_path, "normalized wav")
    return output_path


def mix_timeline_ffmpeg(inputs: list[dict], output_path: str, target_lufs: float = -14.0) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for inp in inputs:
        cmd += ["-i", inp["path"]]

    chains = []
    labels = []
    for idx, inp in enumerate(inputs):
        delay_ms = int(float(inp.get("start", 0)) * 1000)
        vol = float(inp.get("volume", 1.0))
        label = f"a{idx}"
        chains.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}[{label}]")
        labels.append(f"[{label}]")

    filter_complex = (
        ";".join(chains)
        + ";"
        + "".join(labels)
        + f"amix=inputs={len(inputs)}:duration=longest:dropout_transition=0,"
        + f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11[aout]"
    )

    cmd += ["-filter_complex", filter_complex, "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", output_path]
    run_cmd(cmd, "timeline audio mix")
    assert_media(output_path, "timeline mix")
    return output_path
