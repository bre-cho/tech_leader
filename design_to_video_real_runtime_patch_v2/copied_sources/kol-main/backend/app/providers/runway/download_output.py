from __future__ import annotations

import hashlib
from pathlib import Path

import httpx

from app.core.config import settings


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


async def download_runway_output(output_url: str, target_path: str | Path) -> dict:
    """
    Download Runway output video/image to local storage.

    This closes the production artifact loop:
      provider output URL -> local storage file -> checksum -> artifact contract
    """
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    timeout = getattr(settings, "runway_download_timeout_seconds", 300)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(output_url)
        response.raise_for_status()
        path.write_bytes(response.content)

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "checksum": sha256_file(path),
        "mime_type": "video/mp4" if path.suffix.lower() == ".mp4" else "application/octet-stream",
    }
