import io
import json
import logging
from pathlib import Path

import httpx
from PIL import Image

from packages.export_engine.storage import file_sha256, upload_file_to_storage

logger = logging.getLogger("poster_engine.exporter")

EXPORT_SIZES: dict[str, tuple[int, int]] = {
    "poster_4x5": (1080, 1350),
    "square_1x1": (1080, 1080),
    "story_9x16": (1080, 1920),
}

# URL schemes emitted by mock adapters – should never reach real storage.
_MOCK_URL_PREFIXES = ("mock://", "file://")


def _is_real_url(url: str | None) -> bool:
    """Return True when *url* points to a real, downloadable resource."""
    if not url:
        return False
    return not any(url.startswith(prefix) for prefix in _MOCK_URL_PREFIXES)


def _download_image(url: str) -> Image.Image:
    """Download an image from *url* and return a PIL Image object.

    Retries up to 3 times with exponential backoff on transient HTTP or
    network errors so that a brief provider outage does not fail the export.
    """
    import time as _time

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert("RGB")
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            last_exc = exc
            if attempt < 3:
                _time.sleep(2 ** (attempt - 1))
        except httpx.HTTPStatusError as exc:
            # Only retry on 5xx server errors; 4xx are not retryable.
            if exc.response.status_code >= 500 and attempt < 3:
                last_exc = exc
                _time.sleep(2 ** (attempt - 1))
            else:
                raise
    raise RuntimeError(
        f"Failed to download image from {url} after 3 attempts. "
        f"Last error: {last_exc}"
    ) from last_exc


def _resize_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Resize *img* to exactly (target_w × target_h) using cover cropping.

    The image is scaled so that it fully covers the target dimensions, then
    center-cropped to the exact size (no letterboxing / blank borders).
    """
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def export_variant_pack(storage_dir: str, variant: dict) -> dict:
    path = Path(storage_dir) / "exports" / variant["id"]
    path.mkdir(parents=True, exist_ok=True)

    # Prefer the vector/design export URL; fall back to the raster image URL.
    source_url: str | None = None
    if _is_real_url(variant.get("export_url")):
        source_url = variant["export_url"]
    elif _is_real_url(variant.get("image_url")):
        source_url = variant["image_url"]

    # Download the source image once (shared across all sizes).
    source_img: Image.Image | None = None
    if source_url:
        try:
            source_img = _download_image(source_url)
        except Exception as exc:
            logger.warning(
                "export_variant_pack: failed to download source image from %s – "
                "falling back to placeholder. Error: %s",
                source_url,
                exc,
            )

    assets = []
    rendering_status = "ready" if source_img is not None else "placeholder"

    for name, (target_w, target_h) in EXPORT_SIZES.items():
        if source_img is not None:
            resized = _resize_cover(source_img, target_w, target_h)
            local_file = path / f"{name}.png"
            resized.save(str(local_file), format="PNG", optimize=True)
            content_type = "image/png"
            storage_key = (
                f"brands/{variant.get('brand_id', 'unknown')}/"
                f"projects/{variant['project_id']}/variants/{variant['id']}/{name}.png"
            )
        else:
            # Placeholder stub when no real image is available (e.g., mock provider).
            size_str = f"{target_w}x{target_h}"
            local_file = path / f"{name}.txt"
            local_file.write_text(
                f"placeholder export for {variant['id']} size={size_str}\n",
                encoding="utf-8",
            )
            content_type = "text/plain"
            storage_key = (
                f"brands/{variant.get('brand_id', 'unknown')}/"
                f"projects/{variant['project_id']}/variants/{variant['id']}/{name}.txt"
            )

        checksum = file_sha256(local_file)
        upload_result = upload_file_to_storage(local_file, storage_key, content_type=content_type)

        asset_entry: dict = {
            "name": local_file.name,
            "width": target_w,
            "height": target_h,
            "status": rendering_status,
            "mime_type": content_type,
            "checksum": checksum,
            "storage_key": upload_result["storage_key"],
            "signed_url": upload_result["signed_url"],
            "provider": upload_result["provider"],
        }

        # Attach the original provider URLs for auditability.
        if name == "poster_4x5":
            if _is_real_url(variant.get("image_url")):
                asset_entry["source_image_url"] = variant["image_url"]
            if _is_real_url(variant.get("export_url")):
                asset_entry["source_export_url"] = variant["export_url"]

        assets.append(asset_entry)

    manifest = {
        "variant_id": variant["id"],
        "sizes": {name: f"{w}x{h}" for name, (w, h) in EXPORT_SIZES.items()},
        "assets": assets,
        "source_job_id": variant.get("source_job_id"),
        "provider": variant.get("provider"),
        "replayable_input": {
            "canva_design_id": variant.get("canva_design_id"),
            "adobe_asset_id": variant.get("adobe_asset_id"),
        },
        "rendering_status": rendering_status,
    }
    if rendering_status == "placeholder":
        manifest["rendering_note"] = (
            "Local assets are placeholder stubs because no real provider image URL "
            "was available.  Generate with a production provider to get real exports."
        )

    (path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"export_dir": str(path), "manifest": manifest}
