"""Re-export Celery app from core for backward compatibility."""
from app.core.celery_app import celery_app, dispatch_to_dlq

__all__ = ["celery_app", "dispatch_to_dlq"]
