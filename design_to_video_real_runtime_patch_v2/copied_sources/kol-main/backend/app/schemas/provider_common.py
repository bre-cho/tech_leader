from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NormalizedSubmitResult(BaseModel):
    accepted: bool
    provider: str
    provider_model: str | None = None
    provider_request_id: str | None = None
    provider_task_id: str | None = None
    provider_operation_name: str | None = None
    provider_status_raw: str | None = None
    idempotency_key: str | None = None
    latency_ms: int | None = None
    retry_after_seconds: int | None = None
    callback_url_used: str | None = None
    raw_response: dict[str, Any] | None = None
    error_message: str | None = None


class NormalizedStatusResult(BaseModel):
    provider: str
    state: str
    provider_status_raw: str | None = None
    output_video_url: str | None = None
    output_thumbnail_url: str | None = None
    metadata: dict[str, Any] | None = None
    error_message: str | None = None
    failure_code: str | None = None
    failure_category: str | None = None
    raw_response: dict[str, Any] | None = None
    latency_ms: int | None = None
    retry_after_seconds: int | None = None


class NormalizedCallbackEvent(BaseModel):
    provider: str
    event_type: str | None = None
    event_idempotency_key: str
    provider_task_id: str | None = None
    provider_operation_name: str | None = None
    provider_status_raw: str | None = None
    state: str | None = None
    output_video_url: str | None = None
    output_thumbnail_url: str | None = None
    metadata: dict[str, Any] | None = None
    error_message: str | None = None
    failure_code: str | None = None
    failure_category: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
