from __future__ import annotations

from typing import Any


def maybe_enqueue_template_extraction(project: dict[str, Any]) -> None:
    """Compatibility bridge for template extraction hook."""
    if not isinstance(project, dict):
        return
    project.setdefault("template_extracted", False)
