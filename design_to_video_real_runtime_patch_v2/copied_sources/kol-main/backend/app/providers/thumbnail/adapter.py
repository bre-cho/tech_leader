import os
from typing import Any, Dict

from app.providers.base import ProviderAdapter
from app.providers.config import env_bool, provider_default_dry_run
from app.schemas.provider_schema import ProviderName, ProviderStatus


class ThumbnailProviderAdapter(ProviderAdapter):
    provider_name = ProviderName.thumbnail

    def status(self) -> ProviderStatus:
        configured = bool(os.getenv("THUMBNAIL_API_KEY") and os.getenv("THUMBNAIL_API_BASE_URL"))
        enabled = env_bool("THUMBNAIL_PROVIDER_ENABLED", False)

        return ProviderStatus(
            provider=self.provider_name,
            enabled=enabled,
            configured=configured,
            dry_run_default=provider_default_dry_run(),
            message="Thumbnail provider ready for dry-run payload preview."
            if configured else "Thumbnail provider config is missing.",
        )

    def build_payload(self, operation: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "generate_thumbnail":
            return {
                "operation": operation,
                "concept": input_data.get("concept"),
                "title_text": input_data.get("title_text"),
                "style": input_data.get("style", "cinematic_high_ctr"),
                "aspect_ratio": input_data.get("aspect_ratio", "16:9"),
                "reference_assets": input_data.get("reference_assets", []),
            }

        if operation == "rank_thumbnail":
            return {
                "operation": operation,
                "candidates": input_data.get("candidates", []),
                "criteria": input_data.get("criteria", ["clarity", "curiosity", "contrast"]),
            }

        return {"operation": operation, "input": input_data}
