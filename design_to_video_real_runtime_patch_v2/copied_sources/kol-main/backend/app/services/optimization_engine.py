from __future__ import annotations

from copy import deepcopy
from typing import Any


class OptimizationEngine:
    """Compatibility optimization facade for preview payload rewrites."""

    def rewrite_preview_payload(self, payload: dict[str, Any], optimization_response: dict[str, Any] | None) -> dict[str, Any]:
        """Return a safe copy of payload with scenes preserved and optional optimization metadata."""
        safe_payload = deepcopy(payload or {})
        if optimization_response is not None:
            safe_payload["optimization_response"] = deepcopy(optimization_response)
        return safe_payload
