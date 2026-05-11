from __future__ import annotations

from pathlib import Path


def build_audio_preview(*, project_id: str, source_audio_path: str, preview_seconds: int = 15) -> dict:
    # Fallback preview generator: copies input as preview artifact when trimming tooling is unavailable.
    src = Path(source_audio_path)
    if not src.exists():
        raise FileNotFoundError(f"Audio source not found: {source_audio_path}")

    out_dir = Path("./tmp/audio/previews") / project_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "preview.mp3"
    out_path.write_bytes(src.read_bytes())

    return {
        "project_id": project_id,
        "preview_path": str(out_path),
        "preview_seconds": preview_seconds,
        "source_audio_path": source_audio_path,
    }
