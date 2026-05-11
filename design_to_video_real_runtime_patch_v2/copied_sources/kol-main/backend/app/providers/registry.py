"""Low-level Video-Provider routing registry.

This module provides ``build_provider_registry()``, which returns a dict of
:class:`~app.providers.video_router_base.VideoProvider` instances keyed by
provider name.

**Role and scope**
These providers implement a lower-level, synchronous ``requests``-based
interface (``create_task`` / ``get_task``) used by legacy routing code that
pre-dates the async adapter layer.  They are *not* the same as the adapters
in :mod:`app.services.provider_routing.provider_registry`, which provide
higher-level status-check and payload-build capabilities.

If you are looking for the production async adapter registry used by the
render pipeline, see :mod:`app.services.provider_routing.provider_registry`.

**P12 — Seedance vs Seedance2 interface note**
There are two distinct Seedance integration layers in this codebase:

* ``providers/seedance_router.py`` — :class:`SeedanceProvider`
  Implements the **synchronous** :class:`~app.providers.video_router_base.VideoProvider`
  ABC (``create_task`` / ``get_task`` / ``healthcheck`` / ``capability``).
  Used by this registry and the legacy ``/api/video-router`` endpoint.
  Targets the BytePlus Seedance 2.0 API.

* ``providers/seedance2_router.py`` — :class:`Seedance2Provider`
  A second synchronous :class:`~app.providers.video_router_base.VideoProvider`
  adapter for the Seedance2 API (distinct model / cost / latency profile).
  Registered here alongside :class:`SeedanceProvider`.

* ``providers/seedance2/adapter.py`` — :class:`Seedance2Adapter`
  Implements the **async** :class:`~app.services.provider_routing.BaseVideoProviderAdapter`
  interface used by the render pipeline.  Not registered here.

The two ABCs (``VideoProvider`` for sync / ``BaseVideoProviderAdapter`` for
async) are not yet unified.  If you are adding a new provider, prefer the
async ``BaseVideoProviderAdapter`` interface so it integrates with the full
render pipeline, status-check loop, and circuit-breaker layer.  Only add a
new ``VideoProvider`` adapter here if it is needed by the legacy routing path.
"""
from typing import Dict, List

from .video_router_base import VideoProvider
from .seedance_router import SeedanceProvider
from .seedance2_router import Seedance2Provider
from .runway_router import RunwayProvider
from .kling_router import KlingProvider


def build_provider_registry() -> Dict[str, VideoProvider]:
    providers: List[VideoProvider] = [SeedanceProvider(), Seedance2Provider(), RunwayProvider(), KlingProvider()]
    return {p.name: p for p in providers}
