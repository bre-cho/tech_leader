import os
from typing import Any, Dict

from app.providers.base import ProviderAdapter
from app.providers.config import env_bool, provider_default_dry_run
from app.schemas.provider_schema import ProviderName, ProviderStatus


class YouTubeProviderAdapter(ProviderAdapter):
    provider_name = ProviderName.youtube

    def status(self) -> ProviderStatus:
        configured = bool(
            os.getenv("YOUTUBE_CLIENT_ID")
            and os.getenv("YOUTUBE_CLIENT_SECRET")
            and os.getenv("YOUTUBE_REFRESH_TOKEN")
        )
        enabled = env_bool("YOUTUBE_PROVIDER_ENABLED", False)

        return ProviderStatus(
            provider=self.provider_name,
            enabled=enabled,
            configured=configured,
            dry_run_default=provider_default_dry_run(),
            message="YouTube provider ready for dry-run payload preview."
            if configured else "YouTube credentials are not configured.",
        )

    def build_payload(self, operation: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "upload_video":
            return {
                "operation": operation,
                "video_path": input_data.get("video_path"),
                "title": input_data.get("title"),
                "description": input_data.get("description"),
                "tags": input_data.get("tags", []),
                "privacy_status": input_data.get("privacy_status", "private"),
            }

        if operation == "set_thumbnail":
            return {
                "operation": operation,
                "video_id": input_data.get("video_id"),
                "thumbnail_path": input_data.get("thumbnail_path"),
            }

        return {"operation": operation, "input": input_data}
