from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.runtime_paths import render_paths
from app.models.render_job import RenderJob
from app.models.render_scene_task import RenderSceneTask
from app.services.storage_service import get_storage_service


class RenderArtifactError(RuntimeError):
    """Raised when final render artifact creation is not truthful/valid."""


@dataclass(frozen=True)
class FinalRenderArtifact:
    final_video_path: str
    final_video_url: str
    storage_key: str
    storage_bucket: str
    size_bytes: int
    sha256: str
    timeline: dict[str, Any]


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_non_empty_video(path: str) -> None:
    p = Path(path)
    if not p.exists():
        raise RenderArtifactError(f"video file missing: {path}")
    if p.stat().st_size <= 0:
        raise RenderArtifactError(f"video file is empty: {path}")


def _safe_scene_filename(scene: RenderSceneTask) -> str:
    return f"{scene.scene_index:04d}_{scene.id}.mp4"


def _url_to_local_path(url_or_path: str) -> str | None:
    parsed = urlparse(url_or_path)
    if parsed.scheme in {"", "file"}:
        return parsed.path if parsed.scheme == "file" else url_or_path

    public_base = (settings.public_base_url or "").rstrip("/")
    storage_root = Path(settings.storage_root).resolve()
    if public_base and url_or_path.startswith(public_base + "/storage/"):
        rel = url_or_path[len(public_base + "/storage/") :]
        return str(storage_root / rel)
    return None


async def _download_remote_video(url: str, destination: str) -> None:
    # Use a generous timeout for large video downloads.  The default
    # provider_http_timeout is tuned for API calls (short JSON responses);
    # large video files can easily exceed several hundred MB.
    read_timeout = max(300, int(settings.provider_http_timeout_seconds) * 10)
    timeout = httpx.Timeout(connect=30.0, read=float(read_timeout), write=30.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "wb") as handle:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):  # 1 MB chunks
                    handle.write(chunk)
    assert_non_empty_video(destination)


async def materialize_scene_video(scene: RenderSceneTask, work_dir: str) -> str:
    """Return a local, non-empty MP4 path for a succeeded scene.

    Resolution order is strict and auditable:
    1. local_video_path if present
    2. storage_signed_url/public output mapped to local storage if possible
    3. remote URL download
    """
    candidates = [scene.local_video_path, scene.storage_signed_url, scene.output_video_url]
    for candidate in candidates:
        if not candidate:
            continue
        local_candidate = _url_to_local_path(candidate)
        if local_candidate and Path(local_candidate).exists():
            assert_non_empty_video(local_candidate)
            dst = str(Path(work_dir) / _safe_scene_filename(scene))
            shutil.copy2(local_candidate, dst)
            assert_non_empty_video(dst)
            return dst

        parsed = urlparse(candidate)
        if parsed.scheme in {"http", "https"}:
            dst = str(Path(work_dir) / _safe_scene_filename(scene))
            await _download_remote_video(candidate, dst)
            return dst

    raise RenderArtifactError(f"scene {scene.id} has no materializable video artifact")


def run_ffmpeg_concat(scene_paths: list[str], output_path: str) -> None:
    if not scene_paths:
        raise RenderArtifactError("cannot concat empty scene list")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = settings.ffmpeg_binary or "ffmpeg"

    if len(scene_paths) == 1:
        # Keep a real final artifact boundary even for one scene.
        cmd = [ffmpeg, "-y", "-i", scene_paths[0], "-c", "copy", output_path]
        copied = True
    else:
        concat_file = Path(render_paths.concat_scratch_dir) / f"concat_{Path(output_path).stem}.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)
        with open(concat_file, "w", encoding="utf-8") as handle:
            for path in scene_paths:
                escaped = path.replace("'", "'\\''")
                handle.write(f"file '{escaped}'\n")
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            output_path,
        ]
        copied = False

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        if not copied:
            # Fallback when input codecs/timebases are not concat-copy compatible.
            filter_inputs: list[str] = []
            for path in scene_paths:
                filter_inputs.extend(["-i", path])
            filter_complex = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(len(scene_paths)))
            filter_complex += f"concat=n={len(scene_paths)}:v=1:a=1[outv][outa]"
            fallback_cmd = [
                ffmpeg,
                "-y",
                *filter_inputs,
                "-filter_complex",
                filter_complex,
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                "-movflags",
                "+faststart",
                output_path,
            ]
            fallback = subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if fallback.returncode != 0:
                raise RenderArtifactError(f"ffmpeg concat failed: {fallback.stderr[-4000:]}")
        else:
            raise RenderArtifactError(f"ffmpeg copy failed: {result.stderr[-4000:]}")

    assert_non_empty_video(output_path)


async def assemble_render_job_artifacts(job: RenderJob, scenes: list[RenderSceneTask]) -> FinalRenderArtifact:
    ordered = sorted(scenes, key=lambda item: item.scene_index)
    if not ordered:
        raise RenderArtifactError("no successful scenes to assemble")

    final_path = render_paths.episode_output_path(job.project_id, job.id)
    with tempfile.TemporaryDirectory(prefix=f"render_{job.id}_") as work_dir:
        materialized_paths = []
        for scene in ordered:
            materialized_paths.append(await materialize_scene_video(scene, work_dir))

        run_ffmpeg_concat(materialized_paths, final_path)

    # Import lazily to avoid circular import during app startup.
    from app.services.render_quality_truth import assert_final_video_quality

    quality_report = assert_final_video_quality(final_path, expected_aspect_ratio=getattr(job, "aspect_ratio", None))
    size_bytes = Path(final_path).stat().st_size
    checksum = sha256_file(final_path)
    object_key = f"renders/{job.project_id}/{job.id}/final.mp4"
    storage = get_storage_service()
    upload = storage.upload_file(local_path=final_path, object_key=object_key, content_type="video/mp4")

    final_url = upload.get("url") or f"/storage/{object_key}"
    storage_bucket = os.getenv("STORAGE_BUCKET") or os.getenv("GCS_BUCKET") or os.getenv("S3_BUCKET_NAME") or "local"
    timeline = {
        "job_id": job.id,
        "project_id": job.project_id,
        "scene_count": len(ordered),
        "merge_mode": "ffmpeg_concat",
        "final_video_path": final_path,
        "final_video_url": final_url,
        "storage_key": upload.get("storage_key") or object_key,
        "storage_bucket": storage_bucket,
        "size_bytes": size_bytes,
        "sha256": checksum,
        "quality_gate": quality_report.to_dict(),
        "scenes": [
            {
                "scene_task_id": scene.id,
                "scene_index": scene.scene_index,
                "title": scene.title,
                "source_output_video_url": scene.output_video_url,
                "source_local_video_path": scene.local_video_path,
            }
            for scene in ordered
        ],
    }

    manifest_path = Path(render_paths.manifests_dir) / job.project_id / job.id / "final_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    return FinalRenderArtifact(
        final_video_path=final_path,
        final_video_url=final_url,
        storage_key=upload.get("storage_key") or object_key,
        storage_bucket=storage_bucket,
        size_bytes=size_bytes,
        sha256=checksum,
        timeline=timeline,
    )
