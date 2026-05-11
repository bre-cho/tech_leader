"""Prometheus metrics for Celery worker task execution timing.

Usage (inside a Celery task)::

    from app.workers.worker_metrics import record_task_duration

    @celery_app.task(bind=True, ...)
    def my_task(self, ...):
        start = time.monotonic()
        try:
            ...
            record_task_duration(self.name, time.monotonic() - start)
        except Exception:
            record_task_duration(self.name, time.monotonic() - start, failed=True)
            raise

When ``prometheus_client`` is not installed the function is a graceful no-op.
"""
from __future__ import annotations

try:
    import prometheus_client as _prom

    _TASK_DURATION_HISTOGRAM = _prom.Histogram(
        "worker_task_duration_seconds",
        "Duration of Celery worker task execution in seconds",
        ["task_name", "status"],
        buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0],
    )
    _WORKER_METRICS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _WORKER_METRICS_AVAILABLE = False


def record_task_duration(task_name: str, elapsed_seconds: float, *, failed: bool = False) -> None:
    """Record task execution duration in the Prometheus histogram.

    Parameters
    ----------
    task_name:
        Celery task name (``self.name`` inside a bound task).
    elapsed_seconds:
        Wall-clock duration of the task execution.
    failed:
        Set to ``True`` when the task raised an exception so the label
        ``status="failed"`` is recorded separately from ``status="ok"``.
    """
    if not _WORKER_METRICS_AVAILABLE:
        return
    try:
        status = "failed" if failed else "ok"
        _TASK_DURATION_HISTOGRAM.labels(task_name=task_name, status=status).observe(elapsed_seconds)
    except Exception:  # noqa: BLE001
        pass
