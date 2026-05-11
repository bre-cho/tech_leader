from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class YouTubeComplianceResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


def run_youtube_compliance_preflight(payload: dict[str, Any]) -> YouTubeComplianceResult:
    """Validate YouTube publish payload before opening an upload session.

    This is intentionally deterministic and dependency-free. It blocks obvious
    invalid releases before spending quota: missing title/video, overlong title,
    invalid privacy state, made-for-kids flag ambiguity, and missing compliance
    acknowledgement for live publishing.
    """
    errors: list[str] = []
    warnings: list[str] = []
    metadata = payload.get("metadata") or {}
    seo = payload.get("youtube_seo") or {}

    title = str(seo.get("title") or payload.get("title") or payload.get("title_angle") or "").strip()
    description = str(seo.get("description") or metadata.get("description") or payload.get("description") or "")
    final_video_url = str(payload.get("final_video_url") or payload.get("video_url") or metadata.get("final_video_url") or "").strip()
    privacy_status = str(metadata.get("privacy_status") or payload.get("privacy_status") or "public")

    if not title:
        errors.append("youtube.title_missing")
    if len(title) > 100:
        errors.append("youtube.title_over_100_chars")
    if len(description) > 5000:
        errors.append("youtube.description_over_5000_chars")
    if privacy_status not in {"private", "unlisted", "public"}:
        errors.append("youtube.invalid_privacy_status")
    if not final_video_url:
        errors.append("youtube.final_video_url_missing")

    if "made_for_kids" not in metadata and "made_for_kids" not in payload:
        warnings.append("youtube.made_for_kids_not_explicit")

    if privacy_status == "public" and not bool(metadata.get("rights_confirmed") or payload.get("rights_confirmed")):
        errors.append("youtube.rights_confirmation_required_for_public_release")

    return YouTubeComplianceResult(ok=not errors, errors=errors, warnings=warnings)
