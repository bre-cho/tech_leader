"""RenderQualityGate — composite quality scoring for render output.

Phase 2.4: Extended with ``RenderQualityAnalyzer`` which performs a full
vision-quality analysis of a render URL: sharpness, face coverage,
motion blur estimation, and audio sync score.

Phase 2.5 (v16): Added ``VideoQualityAnalyzer`` for real multi-frame temporal
consistency analysis:
- Per-frame sharpness trajectory (detect focus drift across a video)
- Temporal consistency score (measures inter-frame embedding stability)
- Per-axis quality breakdown (lighting, composition, motion)
- Composite quality score with deeper breakdown than the single-frame analyzer

Phase 2.6: Real OpenCV Haar-cascade face detector, ffprobe audio/video sync
proxy, multi-frame trajectory via ``extract_per_frame_qualities()``, and
configurable quality-tier thresholds.
"""
from __future__ import annotations

import json as _json
import logging as _logging
import math
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any

_logger = _logging.getLogger(__name__)

PUBLISH_QUALITY_THRESHOLD = 0.75

# Weights for composite quality score
_IDENTITY_WEIGHT = 0.50
_TEMPORAL_WEIGHT = 0.35
_RESOLUTION_WEIGHT = 0.15

# Per-dimension quality thresholds for remediation hints
_SHARPNESS_THRESHOLD = 0.5
_FACE_COVERAGE_THRESHOLD = 0.3
_MOTION_BLUR_THRESHOLD = 0.5  # above this → too much blur
_AUDIO_SYNC_THRESHOLD = 0.7

# Heuristic bias added to center-region brightness during face coverage estimation.
# This small positive offset accounts for typical face brightness being slightly above
# the mean and helps avoid under-estimating coverage in well-lit renders.
_FACE_COVERAGE_BIAS = 0.1

# Phase 2.5: Number of frames to sample for multi-frame analysis
_VIDEO_QUALITY_N_FRAMES = 12
# Temporal consistency: std-dev threshold above which frames are considered inconsistent
_FRAME_STD_THRESHOLD = 0.15

# ---------------------------------------------------------------------------
# P11: Configurable quality-tier thresholds
# Override via VIDEO_QUALITY_TIER_THRESHOLDS env var (JSON):
#   VIDEO_QUALITY_TIER_THRESHOLDS='{"excellent": 0.85, "good": 0.70, "acceptable": 0.50}'
# ---------------------------------------------------------------------------

def _load_tier_thresholds() -> dict[str, float]:
    """Return quality-tier composite-score boundaries.

    Defaults: excellent ≥ 0.85, good ≥ 0.70, acceptable ≥ 0.50, else poor.
    Override with ``VIDEO_QUALITY_TIER_THRESHOLDS`` JSON env var.
    """
    defaults: dict[str, float] = {"excellent": 0.85, "good": 0.70, "acceptable": 0.50}
    raw = os.getenv("VIDEO_QUALITY_TIER_THRESHOLDS", "").strip()
    if raw:
        try:
            overrides = _json.loads(raw)
            if isinstance(overrides, dict):
                defaults.update({k: float(v) for k, v in overrides.items() if k in defaults})
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "_load_tier_thresholds: malformed JSON in VIDEO_QUALITY_TIER_THRESHOLDS "
                "(%s: %s); using default tier thresholds.",
                type(exc).__name__,
                exc,
            )
    return defaults


def _composite_to_tier(composite: float) -> str:
    """Return the quality tier label for a composite score."""
    thresholds = _load_tier_thresholds()
    if composite >= thresholds["excellent"]:
        return "excellent"
    if composite >= thresholds["good"]:
        return "good"
    if composite >= thresholds["acceptable"]:
        return "acceptable"
    return "poor"



# ---------------------------------------------------------------------------
# P4: ffprobe-based audio/video sync measurement
# ---------------------------------------------------------------------------

def _measure_audio_sync_ffprobe(media_path_or_url: str) -> tuple[float, bool]:
    """Estimate audio/video sync quality using ffprobe stream start-time offset.

    Returns
    -------
    (score, is_stub):
        ``score`` ∈ [0, 1] — 1.0 means perfectly in sync (start_time offset
        < 20 ms); score degrades linearly to 0.0 at a 500 ms offset.
        ``is_stub`` — True when ffprobe is unavailable or the file has no
        audio stream (hardcoded 0.8 fallback is returned in that case).

    The offset heuristic is a proxy only; true A/V sync requires frame-accurate
    analysis.  It is, however, a substantial improvement over the hardcoded 0.8
    stub because it detects files where audio and video streams were muxed with
    a large start-time difference.

    Only ``file://``-style paths and ``http``/``https`` URLs are accepted.
    Other URL schemes (``rtsp://``, ``rtmp://``, …) are rejected and result in
    a stub return to prevent ffprobe from connecting to unintended network
    resources.
    """
    _MAX_OFFSET_MS = 500.0  # offset at which score reaches 0.0
    _EXCELLENT_OFFSET_MS = 20.0  # offset at which score reaches 1.0

    # Scheme validation: only local paths and http(s) URLs are accepted.
    # Reject anything else to prevent ffprobe from following arbitrary
    # network protocols (rtsp://, ftp://, etc.).
    lower = media_path_or_url.lower()
    if lower.startswith(("rtsp://", "rtmp://", "ftp://", "sftp://", "smb://", "data:")):
        return 0.8, True  # unknown/risky scheme → stub

    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "av",  # audio and video streams only
            media_path_or_url,
        ]
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return 0.8, True  # ffprobe failed → return stub

        probe = _json.loads(result.stdout or "{}")
        streams = probe.get("streams", [])

        video_start: float | None = None
        audio_start: float | None = None
        for s in streams:
            codec_type = s.get("codec_type", "")
            raw_start = s.get("start_time")
            if raw_start is None:
                continue
            try:
                t = float(raw_start) * 1000.0  # convert to ms
            except (TypeError, ValueError):
                continue
            if codec_type == "video" and video_start is None:
                video_start = t
            elif codec_type == "audio" and audio_start is None:
                audio_start = t

        if video_start is None or audio_start is None:
            # No audio stream (or no video) — cannot measure sync.
            return 0.8, True

        offset_ms = abs(video_start - audio_start)
        if offset_ms <= _EXCELLENT_OFFSET_MS:
            score = 1.0
        elif offset_ms >= _MAX_OFFSET_MS:
            score = 0.0
        else:
            score = round(
                1.0 - (offset_ms - _EXCELLENT_OFFSET_MS) / (_MAX_OFFSET_MS - _EXCELLENT_OFFSET_MS),
                4,
            )
        return score, False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # ffprobe not installed or timed out.
        return 0.8, True
    except Exception:  # noqa: BLE001
        return 0.8, True


@dataclass
class QualityReport:
    """Composite quality report for a render output.

    ``passed`` is True when ``composite_score >= PUBLISH_QUALITY_THRESHOLD``.
    """

    identity_score: float
    temporal_score: float
    resolution_score: float = 1.0
    composite_score: float = field(init=False)
    passed: bool = field(init=False)
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.composite_score = round(
            self.identity_score * _IDENTITY_WEIGHT
            + self.temporal_score * _TEMPORAL_WEIGHT
            + self.resolution_score * _RESOLUTION_WEIGHT,
            3,
        )
        self.passed = self.composite_score >= PUBLISH_QUALITY_THRESHOLD


class RenderQualityGate:
    """Evaluate render output quality against the publish threshold."""

    def evaluate(
        self,
        identity_score: float,
        temporal_score: float,
        resolution_score: float = 1.0,
    ) -> QualityReport:
        """Compute a composite quality score and return a ``QualityReport``."""
        return QualityReport(
            identity_score=float(identity_score),
            temporal_score=float(temporal_score),
            resolution_score=float(resolution_score),
        )


# ---------------------------------------------------------------------------
# Phase 2.4: Full vision-quality analysis
# ---------------------------------------------------------------------------


class RenderQualityAnalyzer:
    """Analyze a render URL for vision quality metrics.

    ``analyze(render_url)`` returns a dict with:
    - ``sharpness_score``: ∈ [0, 1]  (higher = sharper)
    - ``face_coverage``: ∈ [0, 1]    (fraction of frame with detected face)
    - ``motion_blur_estimate``: ∈ [0, 1]  (higher = more blur)
    - ``audio_sync_score``: ∈ [0, 1]  (higher = better sync; placeholder)
    - ``quality_remediation_hint``: str | None

    Fails gracefully when media is unreachable; returns default 0.5 scores.
    """

    def analyze(self, render_url: str) -> dict[str, Any]:
        """Analyze render_url and return vision quality metrics.

        Audio sync is now measured via ffprobe stream start-time offset when
        ffprobe is available.  When ffprobe is absent or the file has no audio
        stream, ``ALLOW_AUDIO_SYNC_STUB`` must be set in production so operators
        acknowledge that sync is not measured.

        Attempts PIL/OpenCV analysis; falls back to neutral 0.5 defaults
        on any media-processing error so callers always get a usable result.
        """
        try:
            return self._analyze_impl(render_url)
        except RuntimeError:
            raise  # let production stub guards (RuntimeError) propagate
        except Exception:
            return self._fallback_scores(render_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _analyze_impl(self, render_url: str) -> dict[str, Any]:
        """Attempt real quality analysis via PIL/OpenCV/ffprobe."""
        # Audio/video sync via ffprobe start-time offset.
        # Run this FIRST so the stub guard can propagate before any fallible I/O.
        audio_sync_score, audio_sync_score_stub = _measure_audio_sync_ffprobe(render_url)
        if audio_sync_score_stub:
            # Stub guard: enforce operator acknowledgement in production.
            from app.core.production_gate import ensure_stub_allowed  # noqa: PLC0415
            ensure_stub_allowed("Audio A/V sync measurement", allow_env="ALLOW_AUDIO_SYNC_STUB")

        from app.services.avatar.media_embedding_extractor import LocalFrameSampler

        sampler = LocalFrameSampler()
        _, quality_score = sampler.extract_image(render_url)

        # Use quality_score as sharpness proxy from LocalFrameSampler
        sharpness_score = round(quality_score, 4)

        # Face coverage: real OpenCV Haar-cascade detector; brightness heuristic
        # fallback when OpenCV is unavailable.
        face_coverage, face_coverage_stub = self._estimate_face_coverage(render_url)

        # Motion blur: inverse of sharpness (higher blur = lower sharpness)
        motion_blur_estimate = round(1.0 - sharpness_score, 4)

        hint = self._generate_hint(
            sharpness_score=sharpness_score,
            face_coverage=face_coverage,
            motion_blur_estimate=motion_blur_estimate,
            audio_sync_score=audio_sync_score,
        )

        quality_metadata = {
            "sharpness_score": sharpness_score,
            "face_coverage": face_coverage,
            "face_coverage_stub": face_coverage_stub,
            "motion_blur_estimate": motion_blur_estimate,
            "audio_sync_score": audio_sync_score,
            "audio_sync_score_stub": audio_sync_score_stub,
            "render_url": render_url,
        }

        return {
            **quality_metadata,
            "quality_remediation_hint": hint,
            "quality_metadata": quality_metadata,
        }


    def _estimate_face_coverage(self, render_url: str) -> tuple[float, bool]:
        """Detect faces using OpenCV Haar cascades and compute coverage fraction.

        Returns
        -------
        (coverage, is_stub):
            ``coverage`` ∈ [0, 1] — fraction of the frame covered by the
            largest detected face bounding box.
            ``is_stub`` — True when the real detector was unavailable and the
            brightness heuristic fallback was used instead.
        """
        from app.core.production_gate import ensure_stub_allowed  # noqa: PLC0415

        # Download or open the first frame to a temp file for the detector.
        tmp_path: str | None = None
        try:
            import io  # noqa: PLC0415
            import ipaddress  # noqa: PLC0415
            import urllib.request  # noqa: PLC0415
            from urllib.parse import urlparse  # noqa: PLC0415

            if render_url.startswith(("http://", "https://")):
                # SSRF guard: block private/loopback/link-local addresses.
                parsed = urlparse(render_url)
                if parsed.scheme not in ("http", "https") or not parsed.hostname:
                    return 0.5, True
                hostname = parsed.hostname
                try:
                    addr = ipaddress.ip_address(hostname)
                    resolved_addrs = [addr]
                except ValueError:
                    import socket  # noqa: PLC0415
                    try:
                        infos = socket.getaddrinfo(hostname, None)
                        resolved_addrs = [ipaddress.ip_address(info[4][0]) for info in infos]
                    except Exception:  # noqa: BLE001
                        resolved_addrs = []
                for addr in resolved_addrs:
                    if (
                        addr.is_private
                        or addr.is_loopback
                        or addr.is_link_local
                        or addr.is_reserved
                        or addr.is_multicast
                    ):
                        return 0.5, True
                with urllib.request.urlopen(render_url, timeout=10) as resp:  # noqa: S310
                    img_bytes = resp.read()
                fd, tmp_path = tempfile.mkstemp(suffix=".png")
                import os as _os  # noqa: PLC0415
                _os.close(fd)
                with open(tmp_path, "wb") as f:
                    f.write(img_bytes)
            else:
                tmp_path = render_url

            # Attempt real OpenCV Haar-cascade face detection.
            try:
                from app.render.assembly.vision.opencv_face_detector import OpenCVFaceDetector  # noqa: PLC0415
                detector = OpenCVFaceDetector()
                boxes = detector.detect(tmp_path)
                if not boxes:
                    # Detector ran successfully but found no face — legitimate 0.
                    return 0.0, False
                # Use the largest bounding box to compute coverage.
                import cv2 as _cv2  # type: ignore[import]  # noqa: PLC0415
                img = _cv2.imread(tmp_path)
                if img is None:
                    return 0.0, False
                h_img, w_img = img.shape[:2]
                frame_area = max(1, h_img * w_img)
                largest = max(boxes, key=lambda b: b["w"] * b["h"])
                face_area = largest["w"] * largest["h"]
                coverage = round(min(1.0, face_area / frame_area), 4)
                return coverage, False
            except Exception:  # noqa: BLE001
                # OpenCV unavailable or detection failed — fall back to the
                # brightness heuristic and flag it as a stub.
                ensure_stub_allowed("Face coverage measurement", allow_env="ALLOW_FACE_COVERAGE_STUB")
                return self._brightness_face_coverage_fallback(tmp_path), True
        except Exception:  # noqa: BLE001
            return 0.5, True
        finally:
            # Clean up temp file only when we created it (i.e. render_url was a URL).
            if tmp_path is not None and tmp_path != render_url:
                try:
                    import os as _os  # noqa: PLC0415
                    _os.unlink(tmp_path)
                except Exception:  # noqa: BLE001
                    pass

    @staticmethod
    def _brightness_face_coverage_fallback(image_path: str) -> float:
        """PIL brightness heuristic used when OpenCV Haar cascades are unavailable."""
        try:
            from PIL import Image  # type: ignore[import]  # noqa: PLC0415
            img = Image.open(image_path).convert("L").resize((32, 32))
            pixels = list(img.getdata())
            n = len(pixels)
            if n == 0:
                return 0.5
            mid_x, mid_y = 8, 8
            center_pixels = [
                img.getpixel((x, y))
                for x in range(mid_x, 32 - mid_x)
                for y in range(mid_y, 32 - mid_y)
            ]
            overall_mean = sum(pixels) / n
            center_mean = sum(center_pixels) / len(center_pixels) if center_pixels else overall_mean
            return round(min(1.0, max(0.0, center_mean / 255.0 + _FACE_COVERAGE_BIAS)), 4)
        except Exception:  # noqa: BLE001
            return 0.5


    @staticmethod
    def _generate_hint(
        sharpness_score: float,
        face_coverage: float,
        motion_blur_estimate: float,
        audio_sync_score: float,
    ) -> str | None:
        """Generate a remediation hint when any dimension is below threshold."""
        hints = []
        if motion_blur_estimate > _MOTION_BLUR_THRESHOLD:
            hints.append("reduce motion speed to decrease motion blur")
        if sharpness_score < _SHARPNESS_THRESHOLD:
            hints.append("increase render resolution or reduce camera shake")
        if face_coverage < _FACE_COVERAGE_THRESHOLD:
            hints.append("reframe face to ensure avatar is centred in frame")
        if audio_sync_score < _AUDIO_SYNC_THRESHOLD:
            hints.append("verify audio/video sync settings")
        return "; ".join(hints) if hints else None

    @staticmethod
    def _fallback_scores(render_url: str) -> dict[str, Any]:
        """Return neutral 0.5 scores when analysis is not possible.

        The ``_stub`` flag signals callers that this is a fallback result, not
        a real quality measurement — parallel to ``_stub=True`` in
        :func:`~app.distribution.performance_tracker.track_video_performance`.
        """
        quality_metadata = {
            "sharpness_score": 0.5,
            "face_coverage": 0.5,
            "motion_blur_estimate": 0.5,
            "audio_sync_score": 0.5,
            "render_url": render_url,
        }
        return {
            **quality_metadata,
            "_stub": True,
            "quality_remediation_hint": None,
            "quality_metadata": quality_metadata,
        }


# ---------------------------------------------------------------------------
# Phase 2.5: VideoQualityAnalyzer — multi-frame temporal quality analysis
# ---------------------------------------------------------------------------


class VideoQualityAnalyzer:
    """Deep multi-frame quality analysis for rendered video output.

    Unlike ``RenderQualityAnalyzer`` (single-frame proxy), this class samples
    ``_VIDEO_QUALITY_N_FRAMES`` evenly-spaced frames from the video, computes
    per-frame quality vectors, and returns:

    - ``frame_sharpness_trajectory``: sharpness ∈ [0,1] per frame
    - ``temporal_consistency_score``: stability of quality across frames
    - ``focus_drift_detected``: True when sharpness drops > 30 % mid-video
    - ``per_axis_breakdown``: lighting, composition, motion per-axis scores
    - ``composite_quality_score``: weighted aggregate
    - ``quality_tier``: "excellent" | "good" | "acceptable" | "poor"
    - ``remediation_hints``: list of actionable fixes

    Falls back gracefully to neutral scores when media is unreachable or
    frame extraction fails.
    """

    _N_FRAMES = _VIDEO_QUALITY_N_FRAMES

    def analyze_video(self, render_url: str) -> dict[str, Any]:
        """Analyse a video render URL with multi-frame quality scoring.

        Returns a rich quality report dict (see class docstring).
        Falls back to neutral 0.5 scores on any error.
        """
        try:
            return self._analyze_impl(render_url)
        except Exception:
            return self._fallback_report(render_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _analyze_impl(self, render_url: str) -> dict[str, Any]:
        from app.services.avatar.media_embedding_extractor import MediaEmbeddingExtractor

        extractor = MediaEmbeddingExtractor()

        # Use extract_per_frame_qualities() to get a real per-frame quality
        # trajectory.  For images this returns a one-element list; for videos it
        # returns _N_FRAMES evenly-spaced frame quality scores so temporal
        # consistency and focus-drift detection are meaningful.
        is_video = any(
            render_url.lower().endswith(ext)
            for ext in (".mp4", ".mov", ".avi", ".webm")
        )
        n = self._N_FRAMES if is_video else 1
        frame_qualities: list[float] = extractor.extract_per_frame_qualities(render_url, n_frames=n)
        if not frame_qualities:
            frame_qualities = [0.5]

        # Sharpness trajectory
        traj = [round(q, 4) for q in frame_qualities]

        # Temporal consistency: inverse of std-dev across frame qualities
        if len(frame_qualities) > 1:
            mean_q = sum(frame_qualities) / len(frame_qualities)
            std_q = math.sqrt(sum((q - mean_q) ** 2 for q in frame_qualities) / len(frame_qualities))
            temporal_consistency = round(max(0.0, 1.0 - std_q / _FRAME_STD_THRESHOLD), 4)
        else:
            mean_q = frame_qualities[0] if frame_qualities else 0.5
            std_q = 0.0
            temporal_consistency = 1.0

        # Focus drift: check if sharpness in the middle 50% drops below first-frame by > 30%
        focus_drift = False
        if len(traj) >= 4:
            early_mean = sum(traj[: len(traj) // 4]) / max(len(traj) // 4, 1)
            mid_start = len(traj) // 4
            mid_end = 3 * len(traj) // 4
            mid_mean = sum(traj[mid_start:mid_end]) / max(mid_end - mid_start, 1)
            if early_mean > 0 and (early_mean - mid_mean) / early_mean > 0.30:
                focus_drift = True

        # Per-axis breakdown (heuristic proxies from mean quality)
        lighting_score = round(min(1.0, mean_q + 0.1), 4)
        composition_score = round(min(1.0, mean_q), 4)
        motion_score = round(max(0.0, 1.0 - std_q * 2), 4)

        per_axis = {
            "lighting": lighting_score,
            "composition": composition_score,
            "motion_stability": motion_score,
        }

        # Composite
        composite = round(
            0.40 * mean_q + 0.35 * temporal_consistency + 0.25 * motion_score, 4
        )

        # Quality tier — thresholds are configurable via VIDEO_QUALITY_TIER_THRESHOLDS
        tier = _composite_to_tier(composite)

        # Remediation hints
        hints: list[str] = []
        if mean_q < _SHARPNESS_THRESHOLD:
            hints.append("increase render resolution to improve sharpness")
        if focus_drift:
            hints.append("fix camera focus drift — sharpness drops mid-video")
        if temporal_consistency < 0.6:
            hints.append("reduce scene-to-scene lighting/quality variance")
        if motion_score < 0.5:
            hints.append("stabilise camera motion to reduce quality variance")

        return {
            "render_url": render_url,
            "frame_count_analyzed": len(frame_qualities),
            "frame_sharpness_trajectory": traj,
            "temporal_consistency_score": round(temporal_consistency, 4),
            "focus_drift_detected": focus_drift,
            "per_axis_breakdown": per_axis,
            "composite_quality_score": composite,
            "quality_tier": tier,
            "remediation_hints": hints,
        }

    @staticmethod
    def _fallback_report(render_url: str) -> dict[str, Any]:
        """Return neutral report when analysis is not possible.

        The ``_stub`` flag signals callers that this is a fallback result, not
        a real quality measurement.
        """
        return {
            "_stub": True,
            "render_url": render_url,
            "frame_count_analyzed": 0,
            "frame_sharpness_trajectory": [0.5],
            "temporal_consistency_score": 0.5,
            "focus_drift_detected": False,
            "per_axis_breakdown": {"lighting": 0.5, "composition": 0.5, "motion_stability": 0.5},
            "composite_quality_score": 0.5,
            "quality_tier": "acceptable",
            "remediation_hints": [],
        }
