from __future__ import annotations

from typing import Any

from app.models.publish_job import PublishJob
from app.services.publish_providers.base import PublishProviderBase

PUBLISH_MODE_SIMULATED = "SIMULATED"


class SimulatedPublishProvider(PublishProviderBase):
    """Returns a clearly-marked simulated response so QA can identify it in DB.

    This provider must never be used in production or staging environments.
    Any attempt to call ``execute()`` in those environments will raise a
    ``RuntimeError`` to prevent silent no-op publishes from reaching the
    pipeline as if they were real.
    """

    def execute(self, job: PublishJob) -> dict[str, Any]:
        from app.core.production_gate import is_production_or_staging  # noqa: PLC0415

        if is_production_or_staging():
            raise RuntimeError(
                "SimulatedPublishProvider cannot be used in production or staging. "
                "Configure a real publish provider (YouTube, TikTok, Meta) via the "
                "appropriate environment variables and set PUBLISH_PROVIDER_MODE accordingly."
            )
        return {
            "ok": True,
            "mode": PUBLISH_MODE_SIMULATED,
            "provider_publish_id": f"sim-{job.id[:8]}",
            "note": "This is a SIMULATED publish – no real provider was called.",
        }
