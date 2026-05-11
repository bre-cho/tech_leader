from __future__ import annotations

import hashlib
from pathlib import Path

import httpx

from app.core.config import settings


async def cache_remote_video(*, job_id: str, scene_index: int, url: str) -> str:
    """Download a remote video into the render output directory.

    If download fails, create a deterministic empty placeholder file so the
    postprocess worker can handle the fallback path explicitly.
    """

    out_dir = Path(settings.render_output_dir) / str(job_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    token = hashlib.sha256(f"{job_id}:{scene_index}:{url}".encode("utf-8")).hexdigest()[:12]
    out_path = out_dir / f"scene-{int(scene_index):03d}-{token}.mp4"

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            out_path.write_bytes(response.content)
    except Exception:  # noqa: BLE001
        out_path.touch(exist_ok=True)

    return str(out_path)
