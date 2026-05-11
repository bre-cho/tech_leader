"""Legacy /api/video-router endpoints.

These endpoints have been migrated (P2) from the deprecated
``MultiProviderVideoRouter`` to use ``VideoBrainOrchestrator`` for provider
selection so all traffic benefits from EWMA learning and circuit-breaker
protection.

The actual task creation still delegates to the low-level synchronous provider
registry (``app.providers.registry``) because the legacy ``VideoProvider``
adapters own the task-creation I/O logic and have not yet been unified with the
async adapter layer.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.video_router import VideoRouterRequest, VideoRouterResponse
from app.video_engine.brain.capability_registry import default_capabilities

router = APIRouter(prefix="/api/video-router", tags=["video-router"])


class NoProviderAvailable(RuntimeError):
    pass


@router.get("/health")
def video_router_health():
    """Return capability and availability summary for all registered providers.

    Derived from the Brain capability registry so the response is consistent
    with the scoring/routing logic in ``ProviderDecisionEngine``.
    """
    caps = default_capabilities()
    return {
        name: {
            "enabled": True,
            "modes": sorted(cap.modes),
            "quality_bias": cap.quality_bias,
            "estimated_latency_ms": cap.estimated_latency_ms,
            "estimated_cost_per_second": cap.estimated_cost_per_second,
        }
        for name, cap in caps.items()
    }


@router.post("/tasks", response_model=VideoRouterResponse)
def create_video_task(payload: VideoRouterRequest, db: Session = Depends(get_db)):
    """Create a video task, selecting the best provider via ``VideoBrainOrchestrator``.

    Provider selection goes through the Brain scoring engine (EWMA learning +
    capability filtering).  A DB session is injected via FastAPI's dependency
    system so EWMA outcome signals are persisted to the learning loop rather
    than being silently dropped.
    """
    try:
        from app.video_engine.brain.orchestrator import VideoBrainOrchestrator  # noqa: PLC0415
        from app.providers.registry import build_provider_registry  # noqa: PLC0415

        request_dict = payload.model_dump(mode="json")
        mode = request_dict["mode"]

        # Use the Brain orchestrator with the injected session so learning
        # signals are persisted via the DB-backed LearningLoopStore.
        orchestrator = VideoBrainOrchestrator(db=db)
        plan = orchestrator.plan({
            "prompt": request_dict.get("prompt", ""),
            "mode": mode,
            "aspect_ratio": request_dict.get("aspect_ratio", "16:9"),
            "duration_seconds": request_dict.get("duration_seconds", 5),
            "provider": request_dict.get("provider_hint") or "auto",
        })

        selected_provider = plan["selected_provider"]
        fallback_chain = plan.get("fallback_chain", [])

        # Dispatch via the synchronous low-level provider adapter.
        providers = build_provider_registry()
        errors: list[str] = []
        max_retries = 2
        for provider_name in [selected_provider] + [p for p in fallback_chain if p != selected_provider]:
            provider = providers.get(provider_name)
            if provider is None:
                continue
            for attempt in range(max_retries + 1):
                try:
                    task = provider.create_task(request_dict)
                    return {
                        "selected_provider": provider_name,
                        "mode": mode,
                        "task": task,
                        "fallback_chain": fallback_chain,
                    }
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{provider_name}[attempt={attempt}]: {exc}")
                    if attempt >= max_retries:
                        break

        raise NoProviderAvailable("All providers failed: " + " | ".join(errors))

    except NoProviderAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
