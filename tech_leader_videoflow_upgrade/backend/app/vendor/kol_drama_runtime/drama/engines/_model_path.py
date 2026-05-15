"""Shared helper for lazy per-inference model-path resolution in drama engines.

All four drama ML engines (tension, character_intent, subtext, memory_recall)
need to read their model-path environment variable on every inference call so
that a live hot-swap (updating the env var and deploying a new artifact without
a full worker restart) takes effect immediately.

Usage::

    from app.drama.engines._model_path import get_drama_model_path

    def _try_model_score(features):
        path = get_drama_model_path("DRAMA_TENSION_MODEL_PATH")
        if not path:
            return None
        ...
"""
from __future__ import annotations

import os


def get_drama_model_path(env_var: str) -> str:
    """Return the drama model path from *env_var*, re-read on every call.

    The current value of the env var is returned.  If the env var is unset or
    empty, an empty string is returned; callers that captured the original
    module-import-time value in their own ``_MODEL_PATH`` variable should use
    ``get_drama_model_path(env_var) or _MODEL_PATH`` to retain the fallback.

    Parameters
    ----------
    env_var:
        The name of the environment variable, e.g. ``"DRAMA_TENSION_MODEL_PATH"``.

    Returns
    -------
    str
        The resolved artifact path, or an empty string when unconfigured.
    """
    return os.environ.get(env_var, "").strip()
