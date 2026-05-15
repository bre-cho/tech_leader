from __future__ import annotations

import base64
import io
import mimetypes
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image, ImageFilter, ImageOps

from apps.api.core.config import settings
from packages.export_engine.storage import file_sha256, upload_file_to_storage
from packages.provider_adapters.base import ProviderError

TARGET_LONG_EDGE = {"HD": 1920, "4K": 3840, "8K": 7680}


@dataclass
class UpscaleInput:
    image_url: str | None
    image_base64: str | None
    filename: str | None
    target: str
    provider: str
    category: str
    denoise: bool
    sharpen: bool
    face_restore: bool
    preserve_text: bool
    wait: bool = True


def _strip_data_url(value: str) -> str:
    if value.startswith("data:") and "," in value:
        return value.split(",", 1)[1]
    return value


def _guess_extension(filename: str | None, content_type: str | None = None) -> str:
    if filename and "." in filename:
        return Path(filename).suffix.lower()
    if content_type:
        return mimetypes.guess_extension(content_type) or ".png"
    return ".png"


def _target_scale(width: int, height: int, target: str) -> tuple[int, int, int]:
    long_edge = max(width, height)
    wanted = TARGET_LONG_EDGE[target]
    scale = max(1, min(8, round(wanted / long_edge)))
    if long_edge * scale < wanted:
        scale = min(8, scale + 1)
    return width * scale, height * scale, scale


def _enhance_locally(raw: bytes, target: str, sharpen: bool, denoise: bool) -> tuple[bytes, int, int, int]:
    image = Image.open(io.BytesIO(raw))
    image = ImageOps.exif_transpose(image).convert("RGB")
    out_w, out_h, scale = _target_scale(image.width, image.height, target)
    resampling = getattr(Image.Resampling, "LANCZOS", Image.LANCZOS)
    image = image.resize((out_w, out_h), resampling)
    if denoise:
        image = image.filter(ImageFilter.MedianFilter(size=3))
    if sharpen:
        image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=135, threshold=3))
    buf = io.BytesIO()
    image.save(buf, format="WEBP", quality=95, method=6)
    return buf.getvalue(), out_w, out_h, scale


async def _download_image(image_url: str) -> tuple[bytes, str | None]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(image_url)
        response.raise_for_status()
        return response.content, response.headers.get("content-type")


async def _source_bytes(payload: UpscaleInput) -> tuple[bytes, str]:
    if payload.image_base64:
        return base64.b64decode(_strip_data_url(payload.image_base64)), _guess_extension(payload.filename)
    if payload.image_url:
        raw, content_type = await _download_image(payload.image_url)
        return raw, _guess_extension(payload.filename, content_type)
    raise ProviderError("image_upscale", "missing_source", False, "Provide image_url or image_base64")


def _provider_from_auto(category: str) -> str:
    preferred = settings.image_upscale_default_provider.lower()
    if preferred != "auto":
        return preferred
    if settings.claid_api_key:
        return "claid"
    if category in {"portrait", "old_photo"} and settings.picwish_api_key:
        return "picwish"
    if category in {"product", "poster"} and settings.pixelcut_api_key:
        return "pixelcut"
    return "local"


async def upscale_image(payload: UpscaleInput) -> dict:
    provider = _provider_from_auto(payload.category) if payload.provider == "auto" else payload.provider
    if provider == "claid":
        return await _upscale_with_claid(payload)
    if provider == "picwish":
        return await _upscale_with_picwish(payload)
    if provider == "pixelcut":
        return await _upscale_with_pixelcut(payload)
    return await _upscale_with_local(payload)


async def _persist_output(data: bytes, provider: str, target: str, width: int, height: int, scale: int) -> dict:
    job_id = f"up_{uuid4().hex}"
    out_dir = Path(settings.storage_dir) / "image-upscale" / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{target.lower()}-{provider}.webp"
    out_path.write_bytes(data)
    checksum = file_sha256(out_path)
    storage = upload_file_to_storage(out_path, f"image-upscale/{job_id}/{out_path.name}", "image/webp")
    return {
        "job_id": job_id,
        "status": "succeeded",
        "provider": provider,
        "target": target,
        "scale_factor": scale,
        "width": width,
        "height": height,
        "output_url": storage["signed_url"],
        "storage_key": storage["storage_key"],
        "checksum": checksum,
        "metadata": {"storage_provider": storage["provider"], "format": "webp"},
    }


async def _upscale_with_local(payload: UpscaleInput) -> dict:
    raw, _ = await _source_bytes(payload)
    data, width, height, scale = _enhance_locally(raw, payload.target, payload.sharpen, payload.denoise)
    return await _persist_output(data, "local", payload.target, width, height, scale)


async def _upscale_with_claid(payload: UpscaleInput) -> dict:
    if not settings.claid_api_key:
        raise ProviderError("claid", "missing_api_key", False, "CLAID_API_KEY is required")
    # Claid/LetsEnhance is the preferred production API path. The exact API shape
    # can vary by account/version, so keep this adapter isolated behind a stable
    # internal contract and adjust only this file when enabling live mode.
    body = {
        "input": payload.image_url or {"base64": payload.image_base64},
        "operations": {
            "resizing": {"type": "upscale", "target": payload.target.lower()},
            "adjustments": {"sharpen": payload.sharpen, "denoise": payload.denoise},
        },
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            settings.claid_api_base_url.rstrip("/") + "/v1-beta1/image/edit",
            headers={"Authorization": f"Bearer {settings.claid_api_key}", "Content-Type": "application/json"},
            json=body,
        )
    if response.status_code >= 400:
        raise ProviderError("claid", "api_error", response.status_code >= 500, response.text[:500])
    data = response.json()
    return {
        "job_id": data.get("id") or f"up_{uuid4().hex}",
        "status": "succeeded",
        "provider": "claid",
        "target": payload.target,
        "scale_factor": data.get("scale_factor", 0) or 0,
        "width": data.get("width"),
        "height": data.get("height"),
        "output_url": data.get("output", {}).get("tmp_url") or data.get("url"),
        "storage_key": None,
        "checksum": None,
        "metadata": {"raw_provider_response": data},
    }


async def _upscale_with_picwish(payload: UpscaleInput) -> dict:
    if not settings.picwish_api_key:
        raise ProviderError("picwish", "missing_api_key", False, "PICWISH_API_KEY is required")
    body = {
        "image_url": payload.image_url,
        "image_base64": payload.image_base64,
        "sync": payload.wait,
        "scale": 4 if payload.target == "4K" else 8 if payload.target == "8K" else 2,
        "model": "portrait" if payload.face_restore or payload.category == "portrait" else "standard",
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            settings.picwish_api_base_url.rstrip("/") + "/api/tasks/visual/scale",
            headers={"X-API-KEY": settings.picwish_api_key},
            json=body,
        )
    if response.status_code >= 400:
        raise ProviderError("picwish", "api_error", response.status_code >= 500, response.text[:500])
    data = response.json()
    return {
        "job_id": str(data.get("task_id") or data.get("id") or f"up_{uuid4().hex}"),
        "status": "succeeded" if data.get("image") or data.get("result_url") else "processing",
        "provider": "picwish",
        "target": payload.target,
        "scale_factor": body["scale"],
        "width": data.get("width"),
        "height": data.get("height"),
        "output_url": data.get("image") or data.get("result_url"),
        "storage_key": None,
        "checksum": None,
        "metadata": {"raw_provider_response": data},
    }


async def _upscale_with_pixelcut(payload: UpscaleInput) -> dict:
    if not settings.pixelcut_api_key:
        raise ProviderError("pixelcut", "missing_api_key", False, "PIXELCUT_API_KEY is required")
    body = {
        "image_url": payload.image_url,
        "image_base64": payload.image_base64,
        "scale": 4 if payload.target == "4K" else 8 if payload.target == "8K" else 2,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            settings.pixelcut_api_base_url.rstrip("/") + "/upscaler/v1",
            headers={"Authorization": f"Bearer {settings.pixelcut_api_key}"},
            json=body,
        )
    if response.status_code >= 400:
        raise ProviderError("pixelcut", "api_error", response.status_code >= 500, response.text[:500])
    data = response.json()
    return {
        "job_id": str(data.get("id") or f"up_{uuid4().hex}"),
        "status": "succeeded",
        "provider": "pixelcut",
        "target": payload.target,
        "scale_factor": body["scale"],
        "width": data.get("width"),
        "height": data.get("height"),
        "output_url": data.get("url") or data.get("output_url"),
        "storage_key": None,
        "checksum": None,
        "metadata": {"raw_provider_response": data},
    }
