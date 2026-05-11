from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from app.core.async_utils import run_async
from app.providers.seedance import SeedanceClient
from app.workers.celery_app import celery_app, dispatch_to_dlq

_logger = logging.getLogger(__name__)

_MAX_RETRIES = 5
_RETRY_BACKOFF_BASE = 10  # seconds; Celery multiplies by (retry_number + 1)


@celery_app.task(
    name="seedance.poll_task",
    bind=True,
    acks_late=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF_BASE,
)
def poll_seedance_task(self, task_id: str) -> dict:
    try:
        task = run_async(SeedanceClient().poll_until_done(task_id))
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            dispatch_to_dlq(self.name, [task_id], {}, str(exc))
        countdown = _RETRY_BACKOFF_BASE * (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=countdown)

    result = task.model_dump()

    # Persist the completed task result so the video URL survives beyond the
    # Celery result-backend TTL.  We reuse ProviderWebhookEvent as a canonical
    # store for provider-originated artifacts.
    if task.video_url:
        try:
            from app.core.database import SessionLocal  # noqa: PLC0415
            from app.models.provider_webhook_event import ProviderWebhookEvent  # noqa: PLC0415

            idempotency_key = f"seedance.poll.{task.task_id}"
            db = SessionLocal()
            try:
                existing = (
                    db.query(ProviderWebhookEvent)
                    .filter(ProviderWebhookEvent.event_idempotency_key == idempotency_key)
                    .first()
                )
                if existing is None:
                    event = ProviderWebhookEvent(
                        id=str(uuid.uuid4()),
                        provider="seedance",
                        event_type="task_completed",
                        event_idempotency_key=idempotency_key,
                        provider_task_id=task.task_id,
                        signature_valid=True,
                        processed=True,
                        payload_json=json.dumps(result, default=str),
                        normalized_payload_json=json.dumps(
                            {"video_url": task.video_url, "status": task.raw_status},
                            default=str,
                        ),
                        received_at=datetime.now(),
                        processed_at=datetime.now(),
                    )
                    db.add(event)
                    db.commit()
                    _logger.info(
                        "Seedance artifact persisted: task_id=%s video_url=%s",
                        task.task_id,
                        task.video_url,
                    )
            finally:
                db.close()
        except Exception as exc:  # noqa: BLE001
            _logger.error(
                "Failed to persist Seedance artifact for task_id=%s: %s",
                task_id,
                exc,
            )

    return result
