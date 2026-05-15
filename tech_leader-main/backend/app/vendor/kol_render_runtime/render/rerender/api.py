from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.production_gate import ensure_stub_allowed
from app.render.rerender.rerender_execution_service import RerenderExecutionService
from app.render.rerender.schemas import RerenderSceneRequest
from app.render.rerender.rerender_service import RerenderService

router = APIRouter(prefix="/api/v1/render/rerender", tags=["render-rerender"])

_PRODUCTION_ENVS = {"production", "prod", "staging"}


class RerenderRenderJobSceneRequest(BaseModel):
    render_job_id: str
    scene_index: int
    change_type: str = "both"
    override_payload: Optional[dict[str, Any]] = None
    force: bool = False
    smart_reassemble_if_ready: bool = True


def _is_production_like() -> bool:
    env = (getattr(settings, "app_env", None) or getattr(settings, "acse_env", "") or "").lower()
    return env in _PRODUCTION_ENVS


def _legacy_rerender_allowed() -> bool:
    if os.getenv("ALLOW_LEGACY_RERENDER_SCENE", "").lower() in {"1", "true", "yes", "on"}:
        return True
    return not _is_production_like()


def _get_service() -> RerenderService:
    """Legacy manifest rerender service.

    P13 hardlock: this legacy path is dev/backward-compat only. Production
    rerender must go through /render-job/scene so the operation is backed by
    RenderJob/RenderSceneTask, provider dispatch, lineage, Media QA and smart
    reassembly.
    """
    if not _legacy_rerender_allowed():
        raise HTTPException(
            status_code=410,
            detail=(
                "Legacy /api/v1/render/rerender/scene is disabled in production. "
                "Use /api/v1/render/rerender/render-job/scene."
            ),
        )

    try:
        from app.services.tts_service import tts_service as _tts  # type: ignore[import]
        from app.services.video_service import video_service as _video  # type: ignore[import]
    except ImportError:
        ensure_stub_allowed("Rerender TTS/Video stubs", allow_env="ALLOW_RERENDER_STUB")
        # tts_service / video_service are not installed in this deployment.
        # Return 503 so callers get an actionable error instead of a cryptic
        # NotImplementedError 500.  Production traffic must use the supported
        # endpoint: POST /api/v1/render/rerender/render-job/scene
        raise HTTPException(
            status_code=503,
            detail=(
                "Legacy rerender TTS/Video services are not configured in this environment. "
                "Use POST /api/v1/render/rerender/render-job/scene for production rerenders."
            ),
        )

    return RerenderService(tts_service=_tts, video_service=_video)


@router.post("/scene")
def rerender_scene(payload: RerenderSceneRequest) -> Dict[str, Any]:
    try:
        return _get_service().rerender_scene(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/render-job/scene")
def rerender_render_job_scene(payload: RerenderRenderJobSceneRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        return RerenderExecutionService(db).rerender_scene(
            render_job_id=payload.render_job_id,
            scene_index=payload.scene_index,
            change_type=payload.change_type,
            override_payload=payload.override_payload,
            force=payload.force,
            smart_reassemble_if_ready=payload.smart_reassemble_if_ready,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
