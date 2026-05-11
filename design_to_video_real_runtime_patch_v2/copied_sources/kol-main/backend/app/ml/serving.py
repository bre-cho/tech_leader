"""app/ml/serving.py — ML model inference layer for drama engines.

Provides two public functions consumed by drama engines:

- ``predict_from_artifact(path, features, feature_schema)``
    Regression inference (e.g. TensionEngine, CharacterIntentEngine,
    MemoryRecallEngine).  Returns a :class:`PredictResult` with
    ``score ∈ [0, 1]`` and ``stub=False`` on success.

- ``predict_labels_from_artifact(path, features, feature_schema)``
    Multi-label classification (SubtextEngine).  Returns a
    :class:`PredictLabelsResult` with a list of binary int labels and
    ``stub=False`` on success.

Model artifacts are loaded via ``joblib`` and cached in-process so the
model is only deserialized once per worker.  The cache is keyed by
(artifact_path, mtime) so hot-swapping a model file takes effect on the
next worker restart without a code deploy.

Fallback behaviour
------------------
When ``joblib`` is not installed or the artifact file does not exist,
both functions return a result with ``stub=True`` and do not raise.
This preserves the existing heuristic-fallback behaviour in all drama
engines: callers check ``result.stub`` before using the score.

Supported artifact formats
--------------------------
- **joblib** (preferred): any scikit-learn compatible estimator saved via
  ``joblib.dump(model, path)``.  The estimator must implement
  ``predict(X)`` where *X* is a ``(1, n_features)`` numpy array.
  Multi-label classifiers must implement
  ``predict(X) → np.ndarray of shape (1, n_labels)`` or a list of lists.
- **ONNX**: detected by ``.onnx`` suffix.  ``predict_from_artifact`` and
  ``predict_with_onnx`` both accept ``.onnx`` paths; ONNX inference
  requires ``onnxruntime`` (``pip install onnxruntime`` for CPU or
  ``onnxruntime-gpu`` for CUDA).  When ``onnxruntime`` is not installed
  the function falls back gracefully to joblib (if the same path is also
  available as a ``.joblib`` file) and logs a debug message.  See
  :func:`predict_with_onnx` for export instructions.

Feature ordering
----------------
Features are extracted from the *features* dict in the order specified
by *feature_schema* (a list of key names).  Missing keys default to
``0.0``.  This matches the column ordering used by all drama trainers.
"""
from __future__ import annotations

import logging
import os
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger(__name__)
_PROD_LIKE_ENVS = {"production", "prod", "staging"}

try:
    from prometheus_client import Counter as _PromCounter
except ImportError:  # pragma: no cover
    _PromCounter = None  # type: ignore[assignment]

_ML_SERVING_STUB_ACTIVE = (
    _PromCounter(
        "ml_serving_stub_active_total",
        "Count of ML serving stub fallbacks by API and model path.",
        ("api", "model"),
    )
    if _PromCounter is not None
    else None
)


def _warn_stub_if_production(*, api: str, model_path: str, reason: str) -> None:
    if _ML_SERVING_STUB_ACTIVE is not None:
        _ML_SERVING_STUB_ACTIVE.labels(api=api, model=model_path or "unknown").inc()
    app_env = os.getenv("APP_ENV", "").strip().lower()
    if app_env in _PROD_LIKE_ENVS:
        _logger.warning(
            "METRIC ml_serving_stub_active api=%s model=%s app_env=%s reason=%s",
            api,
            model_path or "unknown",
            app_env,
            reason,
        )

# ---------------------------------------------------------------------------
# In-process model cache — LRU eviction with configurable max size
# ---------------------------------------------------------------------------
# Keyed by (artifact_path, mtime_ns) → loaded model object.
# Uses an OrderedDict to implement LRU eviction: on each hit the entry is
# moved to the end (most-recently-used); on a miss a new entry is appended to
# the end, and the oldest entry (front) is evicted when the cache is full.
# Protected by a lock so concurrent workers don't double-load or corrupt order.
#
# Maximum size is configurable via ML_MODEL_CACHE_MAX_SIZE (default: 10).
# Set to 0 to disable the cap entirely (not recommended for hot-swap workloads).
_MODEL_CACHE: OrderedDict[tuple[str, int], Any] = OrderedDict()
_CACHE_LOCK = threading.Lock()

# Validate ML_MODEL_CACHE_MAX_SIZE: must be an integer in [0, 1000].
# Values outside this range suggest a misconfigured deployment.
_ML_MODEL_CACHE_MAX_SIZE_RAW = os.environ.get("ML_MODEL_CACHE_MAX_SIZE", "10")
try:
    _CACHE_MAX_SIZE: int = int(_ML_MODEL_CACHE_MAX_SIZE_RAW)
    if not (0 <= _CACHE_MAX_SIZE <= 1000):
        _logger.warning(
            "ml/serving: ML_MODEL_CACHE_MAX_SIZE=%r is outside the valid range [0, 1000]. "
            "Falling back to default (10). Adjust ML_MODEL_CACHE_MAX_SIZE to a value in [0, 1000].",
            _ML_MODEL_CACHE_MAX_SIZE_RAW,
        )
        _CACHE_MAX_SIZE = 10
except (ValueError, TypeError):
    _logger.warning(
        "ml/serving: ML_MODEL_CACHE_MAX_SIZE=%r is not a valid integer. "
        "Falling back to default (10).",
        _ML_MODEL_CACHE_MAX_SIZE_RAW,
    )
    _CACHE_MAX_SIZE = 10


def _load_artifact(path: str) -> Any:
    """Load and cache a joblib artifact.  Returns the deserialized model.

    If the artifact is a dict with ``__schema_version__`` and ``__model__`` keys
    (written by drama trainers via :func:`save_artifact_with_schema`), the model
    object is extracted from the ``__model__`` key.  This allows downstream
    callers to validate schema compatibility before using the model.
    """
    import joblib  # type: ignore[import]  # noqa: PLC0415

    try:
        mtime_ns = os.stat(path).st_mtime_ns
    except OSError as exc:
        raise FileNotFoundError(f"ml/serving: artifact not found: {path}") from exc

    cache_key = (path, mtime_ns)
    with _CACHE_LOCK:
        if cache_key in _MODEL_CACHE:
            # Move to end to mark as most-recently-used
            _MODEL_CACHE.move_to_end(cache_key)
            return _MODEL_CACHE[cache_key]

    raw = joblib.load(path)
    # Unwrap versioned artifact format: {"__schema_version__": ..., "__model__": model}
    if isinstance(raw, dict) and "__model__" in raw:
        model = raw["__model__"]
        schema_version = raw.get("__schema_version__", "unknown")
        feature_schema = raw.get("__feature_schema__", [])
        _logger.info(
            "ml/serving: loaded versioned artifact %s (schema_version=%s, features=%s, mtime_ns=%d)",
            path,
            schema_version,
            feature_schema,
            mtime_ns,
        )
    else:
        model = raw
    with _CACHE_LOCK:
        # Evict stale entry for the same path if mtime changed
        for k in list(_MODEL_CACHE.keys()):
            if k[0] == path and k != cache_key:
                del _MODEL_CACHE[k]
        _MODEL_CACHE[cache_key] = model
        # Move to end to mark as most-recently-used
        _MODEL_CACHE.move_to_end(cache_key)
        # Evict least-recently-used entries when the cache exceeds max size
        if _CACHE_MAX_SIZE > 0:
            while len(_MODEL_CACHE) > _CACHE_MAX_SIZE:
                evicted_key, _ = _MODEL_CACHE.popitem(last=False)
                _logger.debug("ml/serving: evicted LRU artifact from cache: %s", evicted_key[0])
    _logger.info("ml/serving: loaded artifact %s (mtime_ns=%d)", path, mtime_ns)
    return model


def _build_feature_vector(
    features: dict[str, Any],
    feature_schema: list[str],
) -> Any:
    """Extract feature values in schema order, defaulting missing keys to 0.0."""
    import numpy as np  # noqa: PLC0415

    vec = [float(features.get(name, 0.0)) for name in feature_schema]
    return np.array(vec, dtype=np.float32).reshape(1, -1)


# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------


@dataclass
class PredictResult:
    """Result of a regression ``predict_from_artifact()`` call.

    Attributes
    ----------
    score:
        Predicted scalar ∈ [0, 1].  Undefined when ``stub=True``.
    stub:
        ``True`` when no real inference was performed (artifact missing,
        joblib not installed, or inference error).
    model_path:
        Path of the artifact used, or empty string for stubs.
    """

    score: float = 0.0
    stub: bool = True
    model_path: str = ""


@dataclass
class PredictLabelsResult:
    """Result of a multi-label ``predict_labels_from_artifact()`` call.

    Attributes
    ----------
    labels:
        List of binary int labels (0 or 1), one per output class.
        Empty list when ``stub=True``.
    stub:
        ``True`` when no real inference was performed.
    model_path:
        Path of the artifact used, or empty string for stubs.
    """

    labels: list[int] = field(default_factory=list)
    stub: bool = True
    model_path: str = ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def predict_from_artifact(
    path: str,
    features: dict[str, Any],
    *,
    feature_schema: list[str],
) -> PredictResult:
    """Run regression inference using a joblib artifact.

    Returns a :class:`PredictResult`.  On any error (missing artifact,
    import failure, runtime exception) returns ``PredictResult(stub=True)``
    so callers can fall back gracefully.

    Parameters
    ----------
    path:
        Filesystem path to a ``joblib``-serialised estimator.
    features:
        Dict mapping feature name → numeric value.
    feature_schema:
        Ordered list of feature names that determine column ordering.
    """
    if not path:
        _warn_stub_if_production(api="predict_from_artifact", model_path=path, reason="empty_path")
        return PredictResult(stub=True)
    # Delegate ONNX artifacts to predict_with_onnx() which handles onnxruntime
    # loading and falls back to joblib transparently when onnxruntime is absent.
    if path.endswith(".onnx"):
        return predict_with_onnx(path, features, feature_schema=feature_schema)
    try:
        model = _load_artifact(path)
        X = _build_feature_vector(features, feature_schema)
        raw = model.predict(X)
        # Support both scalar and 1-d/2-d array outputs
        if hasattr(raw, "flat"):
            # numpy array — use flat iterator for safe scalar extraction
            score = float(next(iter(raw.flat)))
        elif hasattr(raw, "__len__") and len(raw) > 0:
            first = raw[0]
            if hasattr(first, "__len__") and len(first) > 0:
                score = float(first[0])
            else:
                score = float(first)
        else:
            score = float(raw)
        # Clamp to [0, 1] and warn if the model returned an out-of-range value.
        clamped = max(0.0, min(1.0, score))
        if clamped != score:
            _logger.warning(
                "ml/serving: score %.6f out of [0, 1] clamped to %.6f for model %s",
                score, clamped, path,
            )
        score = clamped
        return PredictResult(score=score, stub=False, model_path=path)
    except ImportError:
        _logger.debug("ml/serving: joblib not installed; returning stub")
        _warn_stub_if_production(api="predict_from_artifact", model_path=path, reason="joblib_import_error")
        return PredictResult(stub=True)
    except FileNotFoundError:
        _logger.debug("ml/serving: artifact not found at %s; returning stub", path)
        _warn_stub_if_production(api="predict_from_artifact", model_path=path, reason="artifact_missing")
        return PredictResult(stub=True)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("ml/serving: predict_from_artifact failed (%s); returning stub", exc)
        _warn_stub_if_production(api="predict_from_artifact", model_path=path, reason=type(exc).__name__)
        return PredictResult(stub=True)


def predict_labels_from_artifact(
    path: str,
    features: dict[str, Any],
    *,
    feature_schema: list[str],
) -> PredictLabelsResult:
    """Run multi-label classification inference using a joblib artifact.

    Returns a :class:`PredictLabelsResult`.  On any error returns
    ``PredictLabelsResult(stub=True)`` so callers can fall back gracefully.

    Parameters
    ----------
    path:
        Filesystem path to a ``joblib``-serialised multi-label estimator.
    features:
        Dict mapping feature name → numeric value.
    feature_schema:
        Ordered list of feature names that determine column ordering.
    """
    if not path:
        _warn_stub_if_production(api="predict_labels_from_artifact", model_path=path, reason="empty_path")
        return PredictLabelsResult(stub=True)
    try:
        model = _load_artifact(path)
        X = _build_feature_vector(features, feature_schema)
        raw = model.predict(X)
        # raw may be ndarray of shape (1, n_labels) or list of lists
        if hasattr(raw, "tolist"):
            raw_list = raw.tolist()
        else:
            raw_list = list(raw)
        if raw_list and isinstance(raw_list[0], list):
            labels = [int(v) for v in raw_list[0]]
        else:
            labels = [int(v) for v in raw_list]
        return PredictLabelsResult(labels=labels, stub=False, model_path=path)
    except ImportError:
        _logger.debug("ml/serving: joblib not installed; returning stub")
        _warn_stub_if_production(api="predict_labels_from_artifact", model_path=path, reason="joblib_import_error")
        return PredictLabelsResult(stub=True)
    except FileNotFoundError:
        _logger.debug("ml/serving: artifact not found at %s; returning stub", path)
        _warn_stub_if_production(api="predict_labels_from_artifact", model_path=path, reason="artifact_missing")
        return PredictLabelsResult(stub=True)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("ml/serving: predict_labels_from_artifact failed (%s); returning stub", exc)
        _warn_stub_if_production(api="predict_labels_from_artifact", model_path=path, reason=type(exc).__name__)
        return PredictLabelsResult(stub=True)


def predict_with_onnx(
    path: str,
    features: dict[str, Any],
    *,
    feature_schema: list[str],
    input_name: str = "X",
    output_index: int = 0,
) -> PredictResult:
    """Run regression inference using an ONNX model for GPU-accelerated inference.

    Supports both ``.onnx`` files (loaded via ``onnxruntime``) and plain
    ``joblib`` artifacts (falls through to :func:`predict_from_artifact` for
    backward compatibility when the path does not end with ``.onnx``).

    ONNX models exported from sklearn can be created with ``sklearn-onnx``::

        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
        onnx_model = convert_sklearn(
            model,
            initial_types=[("X", FloatTensorType([None, len(feature_schema)]))],
        )
        with open("model.onnx", "wb") as f:
            f.write(onnx_model.SerializeToString())

    When ``onnxruntime`` is not installed this function falls back to
    :func:`predict_from_artifact` transparently so deployments without GPU
    support degrade gracefully to CPU-bound sklearn inference.

    Parameters
    ----------
    path:
        Filesystem path to an ``.onnx`` or ``joblib`` artifact.
    features:
        Dict mapping feature name → numeric value.
    feature_schema:
        Ordered list of feature names that determine column ordering.
    input_name:
        ONNX session input name (default ``"X"``; matches sklearn-to-onnx
        default for the first input).
    output_index:
        Index into the ONNX session output list (default ``0`` for the
        primary prediction output).
    """
    if not path:
        _warn_stub_if_production(api="predict_with_onnx", model_path=path, reason="empty_path")
        return PredictResult(stub=True)
    # Non-ONNX artifacts fall through to the standard joblib path.
    if not path.endswith(".onnx"):
        return predict_from_artifact(path, features, feature_schema=feature_schema)
    try:
        import numpy as np  # noqa: PLC0415
        import onnxruntime as ort  # type: ignore[import]  # noqa: PLC0415

        try:
            mtime_ns = os.stat(path).st_mtime_ns
        except OSError as exc:
            raise FileNotFoundError(f"ml/serving: ONNX artifact not found: {path}") from exc

        cache_key = (path, mtime_ns)
        with _CACHE_LOCK:
            if cache_key in _MODEL_CACHE:
                _MODEL_CACHE.move_to_end(cache_key)
                session = _MODEL_CACHE[cache_key]
            else:
                # Configure ONNX Runtime session — prefer GPU (CUDA) when available,
                # fall back to CPU transparently.
                providers: list[str] = []
                try:
                    available = ort.get_available_providers()
                    if "CUDAExecutionProvider" in available:
                        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
                    else:
                        providers = ["CPUExecutionProvider"]
                except Exception:  # noqa: BLE001
                    providers = ["CPUExecutionProvider"]
                session = ort.InferenceSession(path, providers=providers)
                for k in list(_MODEL_CACHE.keys()):
                    if k[0] == path and k != cache_key:
                        del _MODEL_CACHE[k]
                _MODEL_CACHE[cache_key] = session
                _MODEL_CACHE.move_to_end(cache_key)
                if _CACHE_MAX_SIZE > 0:
                    while len(_MODEL_CACHE) > _CACHE_MAX_SIZE:
                        evicted_key, _ = _MODEL_CACHE.popitem(last=False)
                        _logger.debug(
                            "ml/serving: evicted LRU ONNX session from cache: %s", evicted_key[0]
                        )
                _logger.info("ml/serving: loaded ONNX artifact %s", path)

        X = _build_feature_vector(features, feature_schema)
        outputs = session.run(None, {input_name: X})
        raw = outputs[output_index]
        if hasattr(raw, "flat"):
            score = float(next(iter(raw.flat)))
        elif hasattr(raw, "__len__") and len(raw) > 0:
            first = raw[0]
            score = float(first[0] if hasattr(first, "__len__") and len(first) > 0 else first)
        else:
            score = float(raw)
        score = max(0.0, min(1.0, score))
        return PredictResult(score=score, stub=False, model_path=path)
    except ImportError:
        _logger.debug("ml/serving: onnxruntime not installed; falling back to joblib predict")
        return predict_from_artifact(path, features, feature_schema=feature_schema)
    except FileNotFoundError:
        _logger.debug("ml/serving: ONNX artifact not found at %s; returning stub", path)
        _warn_stub_if_production(api="predict_with_onnx", model_path=path, reason="artifact_missing")
        return PredictResult(stub=True)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("ml/serving: predict_with_onnx failed (%s); returning stub", exc)
        _warn_stub_if_production(api="predict_with_onnx", model_path=path, reason=type(exc).__name__)
        return PredictResult(stub=True)


def invalidate_model_cache(path: str | None = None) -> None:
    """Evict cached model(s) from the in-process cache.

    Parameters
    ----------
    path:
        Specific artifact path to evict.  When ``None`` all cached models
        are cleared (useful in tests or after a manual model swap).
    """
    with _CACHE_LOCK:
        if path is None:
            _MODEL_CACHE.clear()
        else:
            for k in list(_MODEL_CACHE.keys()):
                if k[0] == path:
                    del _MODEL_CACHE[k]


def save_artifact_with_schema(
    model: Any,
    path: str,
    *,
    schema_version: str,
    feature_schema: list[str],
    extra_metadata: dict[str, Any] | None = None,
) -> None:
    """Serialise *model* as a versioned artifact bundle via ``joblib``.

    The bundle is a plain dict with the following keys so it can be loaded by
    ``_load_artifact()`` and validated for schema compatibility:

    * ``__schema_version__``: caller-supplied string (e.g. ``"tension_v1"``).
    * ``__feature_schema__``: ordered list of feature column names.
    * ``__model__``: the serialised sklearn/joblib estimator object.
    * ``__metadata__``: optional extra metadata dict for audit trails.

    Parameters
    ----------
    model:
        A fitted sklearn-compatible estimator.
    path:
        Output file path.  Parent directories are created automatically.
    schema_version:
        Human-readable schema identifier, e.g. ``"tension_v1"``.  Should be
        bumped whenever ``feature_schema`` changes to catch mis-deployments.
    feature_schema:
        Ordered list of feature names used during training.  Must match the
        ordering in :func:`_build_feature_vector` at inference time.
    extra_metadata:
        Optional dict serialised alongside the model for audit/lineage.
    """
    import joblib  # type: ignore[import]  # noqa: PLC0415
    import pathlib  # noqa: PLC0415

    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "__schema_version__": schema_version,
        "__feature_schema__": list(feature_schema),
        "__model__": model,
        "__metadata__": extra_metadata or {},
    }
    joblib.dump(bundle, path)
    _logger.info(
        "ml/serving: saved versioned artifact %s (schema_version=%s, features=%s)",
        path,
        schema_version,
        feature_schema,
    )


def validate_artifact_schema(
    path: str,
    *,
    expected_schema_version: str | None = None,
    expected_feature_schema: list[str] | None = None,
) -> dict[str, Any]:
    """Load an artifact and validate its schema metadata.

    Returns a dict with ``schema_version``, ``feature_schema``, and
    ``schema_ok`` (bool).  Does not raise; callers should check ``schema_ok``
    and log/alert when ``False``.

    Parameters
    ----------
    path:
        Path to a ``joblib``-serialised artifact bundle.
    expected_schema_version:
        When supplied, compared to the stored ``__schema_version__``.
    expected_feature_schema:
        When supplied, compared to the stored ``__feature_schema__``.
    """
    try:
        import joblib  # type: ignore[import]  # noqa: PLC0415

        raw = joblib.load(path)
        if not isinstance(raw, dict) or "__model__" not in raw:
            return {
                "schema_version": None,
                "feature_schema": None,
                "schema_ok": False,
                "error": "not a versioned artifact bundle (missing __model__ key)",
            }
        stored_version = raw.get("__schema_version__")
        stored_schema = raw.get("__feature_schema__", [])
        version_ok = (
            expected_schema_version is None
            or stored_version == expected_schema_version
        )
        schema_ok = (
            expected_feature_schema is None
            or stored_schema == expected_feature_schema
        ) and version_ok
        return {
            "schema_version": stored_version,
            "feature_schema": stored_schema,
            "schema_ok": schema_ok,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "schema_version": None,
            "feature_schema": None,
            "schema_ok": False,
            "error": str(exc),
        }
