from typing import Any, Dict

from app.providers.base import ProviderAdapter
from app.schemas.provider_schema import ProviderName, ProviderStatus


class SimulatedProviderAdapter(ProviderAdapter):
    """Simulated video provider for local / test environments only.

    Both ``status()`` and ``build_payload()`` raise ``RuntimeError`` when
    called in production or staging so the simulated provider can never
    silently short-circuit a real pipeline without an explicit emergency bypass.
    """

    provider_name = ProviderName.simulated

    def status(self) -> ProviderStatus:
        from app.core.production_gate import is_production_or_staging  # noqa: PLC0415

        if is_production_or_staging():
            raise RuntimeError(
                "SimulatedProviderAdapter cannot be used in production or staging. "
                "Configure a real video provider and remove 'simulated' from the provider registry."
            )
        return ProviderStatus(
            provider=self.provider_name,
            enabled=True,
            configured=True,
            dry_run_default=True,
            message="Simulated provider is always available for local tests.",
        )

    def build_payload(self, operation: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.core.production_gate import is_production_or_staging  # noqa: PLC0415

        if is_production_or_staging():
            raise RuntimeError(
                "SimulatedProviderAdapter.build_payload() is disabled in production or staging. "
                "Use a real video provider adapter."
            )
        return {
            "operation": operation,
            "input": input_data,
            "simulated": True,
        }
