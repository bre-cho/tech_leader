"""ProviderAdapter registry for the production render pipeline.

This module provides :class:`ProviderRegistry`, which maps
:class:`~app.schemas.provider_schema.ProviderName` values to
:class:`~app.providers.base.ProviderAdapter` instances.

**Role and scope**
These adapters implement higher-level ``status()`` / ``build_payload()``
operations and are used by the provider health-check and status-reporting
layer (not by the async render submit/query path).

For the lower-level, synchronous ``VideoProvider``-based registry used by
legacy routing code, see :mod:`app.providers.registry`.

**SimulatedProviderAdapter** is excluded in production/staging environments.
Calling ``.get(ProviderName.simulated)`` in those environments raises
:class:`KeyError`.  The individual adapter methods also raise
:class:`RuntimeError` on their own, but excluding it from the registry avoids
even instantiating it at startup in a production-like context.
"""
from app.providers.base import ProviderAdapter
from app.providers.thumbnail.adapter import ThumbnailProviderAdapter
from app.providers.veo.adapter import VeoProviderAdapter
from app.providers.volcengine.adapter import VolcengineProviderAdapter
from app.providers.youtube.adapter import YouTubeProviderAdapter
from app.schemas.provider_schema import ProviderName


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[ProviderName, ProviderAdapter] = {
            ProviderName.youtube: YouTubeProviderAdapter(),
            ProviderName.veo: VeoProviderAdapter(),
            ProviderName.thumbnail: ThumbnailProviderAdapter(),
            ProviderName.volcengine: VolcengineProviderAdapter(),
        }

        # Include the simulated adapter only in non-production-like environments.
        # In production/staging it is excluded entirely so the registry never
        # surfaces it through status reports or health checks.
        from app.core.production_gate import is_production_or_staging  # noqa: PLC0415

        if not is_production_or_staging():
            from app.providers.simulated import SimulatedProviderAdapter  # noqa: PLC0415

            self._providers[ProviderName.simulated] = SimulatedProviderAdapter()

    def get(self, provider: ProviderName) -> ProviderAdapter:
        return self._providers[provider]

    def all(self) -> list[ProviderAdapter]:
        return list(self._providers.values())


provider_registry = ProviderRegistry()
