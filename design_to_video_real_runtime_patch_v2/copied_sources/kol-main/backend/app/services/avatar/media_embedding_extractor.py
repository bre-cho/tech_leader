from __future__ import annotations

"""Production avatar media embedding extractor.

Priority:
1. Remote model endpoint MEDIA_EMBEDDING_MODEL_ENDPOINT.
2. Local CLIP/OpenCLIP/SentenceTransformers image model, when installed.
3. OpenCV/PIL statistical embedding only in non-production or when explicitly allowed.
4. SHA-256 deterministic stub only outside production or emergency bypass.

Production should configure a real model endpoint or install a real embedding
model dependency. This file keeps local dev usable while preventing silent hash
identity checks in production.
"""

import base64
import hashlib
import json
import logging
import math
import os
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from app.core.production_gate import ensure_stub_allowed, env_bool, is_production_or_staging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter as _PromCounter
except ImportError:  # pragma: no cover
    _PromCounter = None  # type: ignore[assignment]

_AVATAR_EMBEDDING_STUB_ACTIVE = (
    _PromCounter(
        "avatar_embedding_stub_active_total",
        "Count of times avatar embedding fell back to stub hashing.",
    )
    if _PromCounter is not None
    else None
)

_MODEL_ENDPOINT = os.environ.get("MEDIA_EMBEDDING_MODEL_ENDPOINT", "")
_EMBEDDING_DIM = int(os.environ.get("MEDIA_EMBEDDING_DIM", "128"))
_OPENCV_MIN_QUALITY = 0.25


class ExtractionFallbackRequired(RuntimeError):
    pass


def _record_stub_fallback(reason: str) -> None:
    if _AVATAR_EMBEDDING_STUB_ACTIVE is not None:
        _AVATAR_EMBEDDING_STUB_ACTIVE.inc()
    logger.warning("Avatar embedding stub fallback activated: %s", reason)


def _stub_embedding(data: bytes) -> list[float]:
    digest = hashlib.sha256(data).digest()
    extended = (digest * math.ceil(_EMBEDDING_DIM / len(digest)))[:_EMBEDDING_DIM]
    raw = [float(b) / 255.0 for b in extended]
    norm = math.sqrt(sum(x * x for x in raw)) or 1.0
    return [round(x / norm, 6) for x in raw]


def _ensure_stub_allowed() -> None:
    if is_production_or_staging() and (
        env_bool("ALLOW_AVATAR_EMBEDDING_STUB", False) or env_bool("ALLOW_STUB_EMBEDDING", False)
    ):
        _record_stub_fallback("stub_allowed_in_production_or_staging")
        if env_bool("IDENTITY_GATE_STRICT", False):
            raise RuntimeError(
                "Avatar embedding stub is disabled when IDENTITY_GATE_STRICT=true. "
                "Configure MEDIA_EMBEDDING_MODEL_ENDPOINT or install a real embedding model."
            )
    if env_bool("ALLOW_AVATAR_EMBEDDING_STUB", False) or env_bool("ALLOW_STUB_EMBEDDING", False):
        return
    ensure_stub_allowed("Avatar embedding stub", allow_env="ALLOW_AVATAR_EMBEDDING_STUB")


def _ensure_lightweight_allowed() -> None:
    if is_production_or_staging() and not env_bool("ALLOW_LIGHTWEIGHT_AVATAR_EMBEDDING", False):
        raise RuntimeError(
            "Lightweight avatar embedding is disabled in production/staging. Configure "
            "MEDIA_EMBEDDING_MODEL_ENDPOINT or install CLIP/OpenCLIP; set "
            "ALLOW_LIGHTWEIGHT_AVATAR_EMBEDDING=true only for temporary bypass."
        )


def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(float(x) / norm, 6) for x in vec]


class LocalFrameSampler:
    def extract_image(self, source: str) -> tuple[list[float], float]:
        from PIL import Image  # type: ignore[import]
        import io

        if source.startswith(("http://", "https://")):
            with urllib.request.urlopen(source, timeout=10) as resp:  # noqa: S310
                img_bytes = resp.read()
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        else:
            img = Image.open(source).convert("RGB")
        return self.extract_pil_image(img)

    def extract_pil_image(self, img: Any) -> tuple[list[float], float]:
        img = img.convert("RGB").resize((16, 16))
        pixels = list(img.getdata())
        r_vals = [p[0] for p in pixels]
        g_vals = [p[1] for p in pixels]
        b_vals = [p[2] for p in pixels]
        gray_vals = [(p[0] * 0.299 + p[1] * 0.587 + p[2] * 0.114) for p in pixels]

        def stats(vals: list[float]) -> list[float]:
            n = len(vals)
            mean = sum(vals) / n
            std = math.sqrt(sum((v - mean) ** 2 for v in vals) / n) if n > 1 else 0.0
            return [mean / 255.0, std / 255.0]

        features = stats(r_vals) * 32 + stats(g_vals) * 32 + stats(b_vals) * 32
        features = (features + [0.0] * _EMBEDDING_DIM)[:_EMBEDDING_DIM]
        quality = _compute_quality(gray_vals)
        return _normalize(features), quality


def _compute_quality(gray_pixels: list[float]) -> float:
    if not gray_pixels:
        return 0.0
    n = len(gray_pixels)
    mean = sum(gray_pixels) / n
    variance = sum((p - mean) ** 2 for p in gray_pixels) / n
    std = math.sqrt(variance)
    sharpness = min(1.0, std / 64.0)
    brightness = 1.0 - abs(mean / 255.0 - 0.5) * 2.0
    return round(sharpness * 0.6 + brightness * 0.4, 4)


class MediaEmbeddingExtractor:
    def __init__(self) -> None:
        self._local_sampler = LocalFrameSampler()
        self._last_extraction: dict[str, Any] = {
            "extraction_source": "uninitialized",
            "quality_score_cap": 0.0,
            "needs_reverification": True,
            "quality_score": 0.0,
        }

    def extract(self, media_path_or_url: str, n_frames: int = 8) -> list[float]:
        return self.extract_with_quality(media_path_or_url, n_frames=n_frames)[0]

    def extract_with_quality(self, media_path_or_url: str, n_frames: int = 8) -> tuple[list[float], float]:
        if _MODEL_ENDPOINT:
            try:
                emb = self._model_extract(media_path_or_url, n_frames)
                self._record("model_endpoint", 1.0, False, 1.0)
                return emb, 1.0
            except Exception as exc:
                if is_production_or_staging():
                    raise RuntimeError(f"MEDIA_EMBEDDING_MODEL_ENDPOINT failed: {exc}") from exc

        try:
            emb, q = self._clip_extract(media_path_or_url, n_frames)
            self._record("clip", 1.0, False, q)
            return emb, q
        except Exception as exc:
            logger.warning("Avatar embedding clip extraction failed: %s", exc)
            if is_production_or_staging() and not env_bool("ALLOW_LIGHTWEIGHT_AVATAR_EMBEDDING", False):
                raise

        try:
            _ensure_lightweight_allowed()
            emb, q, source = self._local_extract(media_path_or_url, n_frames)
            self._record(source, 0.8, True, q)
            return emb, q
        except Exception as exc:
            logger.warning("Avatar embedding lightweight extraction failed: %s", exc)

        _ensure_stub_allowed()
        quality = 0.4
        self._record("stub", 0.4, True, quality)
        _record_stub_fallback("all_embedding_extractors_failed")
        return self._stub_extract(media_path_or_url, n_frames), quality

    def extract_per_frame_qualities(self, media_path_or_url: str, n_frames: int = 8) -> list[float]:
        """Return a list of per-frame quality scores ∈ [0, 1].

        For images a one-element list is returned.  For videos *n_frames*
        evenly-spaced frames are sampled and a quality score is computed for
        each one, giving callers a quality *trajectory* rather than a single
        aggregate value.

        Falls back to ``[0.5] * n_frames`` when frame extraction fails so
        callers (e.g. :class:`VideoQualityAnalyzer`) always receive a
        usable list regardless of media availability.
        """
        lower = media_path_or_url.lower()
        is_video = lower.endswith((".mp4", ".mov", ".avi", ".webm", ".mkv"))
        if not is_video:
            try:
                _, q = self._local_sampler.extract_image(media_path_or_url)
                return [q]
            except Exception:
                return [0.5]

        # Sample n_frames from the video via OpenCV.
        try:
            paths = self._materialize_sample_images(media_path_or_url, n_frames)
            qualities: list[float] = []
            for path in paths:
                try:
                    _, q = self._local_sampler.extract_image(str(path))
                    qualities.append(q)
                except Exception:
                    qualities.append(0.5)
                finally:
                    try:
                        Path(path).unlink(missing_ok=True)
                    except Exception as cleanup_exc:  # noqa: BLE001
                        logger.debug("Failed to cleanup sampled frame %s: %s", path, cleanup_exc)
            return qualities if qualities else [0.5] * max(1, n_frames)
        except Exception as exc:  # noqa: BLE001
            logger.warning("extract_per_frame_qualities fallback due to error: %s", exc)
            return [0.5] * max(1, n_frames)

    def get_last_extraction_info(self) -> dict[str, Any]:
        return dict(self._last_extraction)

    def _record(self, source: str, cap: float, needs_reverification: bool, quality: float) -> None:
        self._last_extraction = {
            "extraction_source": source,
            "quality_score_cap": cap,
            "needs_reverification": needs_reverification,
            "quality_score": quality,
        }

    def _model_extract(self, media_path_or_url: str, n_frames: int) -> list[float]:
        payload = {"media_url": media_path_or_url, "n_frames": n_frames, "output_dim": _EMBEDDING_DIM}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(_MODEL_ENDPOINT, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=int(os.getenv("MEDIA_EMBEDDING_TIMEOUT", "20"))) as resp:  # noqa: S310
            result: dict[str, Any] = json.loads(resp.read())
        return _normalize([float(x) for x in result["embedding"]])

    def _clip_extract(self, media_path_or_url: str, n_frames: int) -> tuple[list[float], float]:
        # Prefer sentence-transformers CLIP because it is simple CPU-safe when installed.
        try:
            from PIL import Image  # type: ignore[import]
            from sentence_transformers import SentenceTransformer  # type: ignore[import]
        except Exception as exc:
            raise ExtractionFallbackRequired("clip_dependencies_missing") from exc

        image_paths = self._materialize_sample_images(media_path_or_url, n_frames)
        model_name = os.getenv("AVATAR_EMBEDDING_MODEL", "clip-ViT-B-32")
        model = SentenceTransformer(model_name)
        vectors: list[list[float]] = []
        qualities: list[float] = []
        sampler = LocalFrameSampler()
        for path in image_paths:
            img = Image.open(path).convert("RGB")
            vectors.append([float(x) for x in model.encode(img).tolist()])
            _, q = sampler.extract_pil_image(img)
            qualities.append(q)
        for path in image_paths:
            if str(path).startswith(tempfile.gettempdir()):
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception as cleanup_exc:  # noqa: BLE001
                    logger.debug("Failed to cleanup temporary clip image %s: %s", path, cleanup_exc)
        if not vectors:
            raise ExtractionFallbackRequired("clip_no_vectors")
        return self._average(vectors), round(sum(qualities) / max(1, len(qualities)), 4)

    def _local_extract(self, media_path_or_url: str, n_frames: int) -> tuple[list[float], float, str]:
        lower = media_path_or_url.lower()
        is_video = lower.endswith((".mp4", ".mov", ".avi", ".webm", ".mkv"))
        if is_video:
            emb, q = self._opencv_extract(media_path_or_url, n_frames)
            return emb, q, "opencv_lightweight"
        emb, q = self._local_sampler.extract_image(media_path_or_url)
        return emb, q, "pil_lightweight"

    def _materialize_sample_images(self, media_path_or_url: str, n_frames: int) -> list[Path]:
        lower = media_path_or_url.lower()
        if not lower.endswith((".mp4", ".mov", ".avi", ".webm", ".mkv")):
            return [Path(media_path_or_url)]
        import cv2  # type: ignore[import]

        cap = cv2.VideoCapture(media_path_or_url)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        idxs = [min(total - 1, int(round(i * (total - 1) / max(1, n_frames - 1)))) for i in range(max(1, n_frames))]
        paths: list[Path] = []
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                continue
            path = Path(tempfile.mkstemp(suffix=".png")[1])
            cv2.imwrite(str(path), frame)
            paths.append(path)
        cap.release()
        return paths

    def _opencv_extract(self, video_path: str, n_frames: int) -> tuple[list[float], float]:
        paths = self._materialize_sample_images(video_path, n_frames)
        embs: list[list[float]] = []
        qs: list[float] = []
        for path in paths:
            try:
                emb, q = self._local_sampler.extract_image(str(path))
                if q >= _OPENCV_MIN_QUALITY:
                    embs.append(emb)
                    qs.append(q)
            finally:
                try:
                    path.unlink(missing_ok=True)
                except Exception as cleanup_exc:  # noqa: BLE001
                    logger.debug("Failed to cleanup OpenCV frame %s: %s", path, cleanup_exc)
        if not embs:
            raise ExtractionFallbackRequired("opencv_no_frames")
        return self._average(embs), round(sum(qs) / len(qs), 4)

    def _stub_extract(self, media_path_or_url: str, n_frames: int) -> list[float]:
        lower = media_path_or_url.lower()
        if lower.endswith((".mp4", ".mov", ".avi", ".webm", ".mkv")):
            return self._average([_stub_embedding(f"{media_path_or_url}:frame:{i}".encode()) for i in range(n_frames)])
        return _stub_embedding(media_path_or_url.encode())

    @staticmethod
    def _average(embeddings: list[list[float]]) -> list[float]:
        dim = len(embeddings[0]) if embeddings else _EMBEDDING_DIM
        avg = [sum(e[i] for e in embeddings) / len(embeddings) for i in range(dim)]
        return _normalize(avg)
