from __future__ import annotations

from app.providers.base import BaseVideoProviderAdapter
from app.services.provider_router import get_provider_adapter as get_canonical_provider_adapter


def get_provider_adapter(provider: str) -> BaseVideoProviderAdapter:
    """Compatibility shim delegating provider lookup to the canonical router."""
    return get_canonical_provider_adapter(provider)
