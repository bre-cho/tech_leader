from __future__ import annotations

from contextlib import closing
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.storyboard_engine.schemas import CampaignBrief, PosterInput, ProviderName, StoryboardVariant
from app.storyboard_to_render_bridge import RenderHandoffOptions, StoryboardToRenderBridge
from app.db.session import SessionLocal
from app.services.render_orchestrator import RenderOrchestrator

router = APIRouter(prefix="/api/poster-video", tags=["Poster To Video Render"])

_SUPPORTED_PROVIDERS = {"veo", "runway", "kling", "seedance", "seedance2", "volcengine"}


class PosterVideoRenderRequest(BaseModel):
    """Flat request for the standard poster -> render pipeline."""

    poster_image_url: Optional[str] = None
    poster_image_base64: Optional[str] = None
    campaign_brief: CampaignBrief
    providers: List[str] = Field(default_factory=lambda: ["veo", "runway", "kling", "seedance2"])
    include_audio: bool = True
    include_smart_subtitle: bool = True
    include_avatar: bool = True
    include_drama: bool = True
    include_voice_clone: bool = False
    render_mode: str = "provider_ai_video"
    execution_mode: Literal["dry_run", "execute"] = "dry_run"
    requested_variants: List[StoryboardVariant] = Field(default_factory=lambda: [StoryboardVariant.conversion])

    def to_poster_input(self) -> PosterInput:
        valid_providers = [
            ProviderName(p.lower())
            for p in self.providers
            if p.lower() in {e.value for e in ProviderName}
        ]
        if not valid_providers:
            valid_providers = [ProviderName.veo, ProviderName.kling]

        return PosterInput(
            poster_image_url=self.poster_image_url,
            poster_image_base64=self.poster_image_base64,
            campaign_brief=self.campaign_brief,
            requested_variants=self.requested_variants,
            providers=valid_providers,
        )

    def to_handoff_options(self) -> RenderHandoffOptions:
        providers = [p.lower() for p in self.providers if p.lower() in _SUPPORTED_PROVIDERS]
        if not providers:
            providers = ["veo", "kling"]
        return RenderHandoffOptions(
            providers=providers,
            aspect_ratio=self.campaign_brief.aspect_ratio,
            render_mode=self.render_mode,
            include_audio=self.include_audio,
            include_avatar=self.include_avatar,
            include_drama=self.include_drama,
            include_voice_clone=self.include_voice_clone,
            include_smart_subtitle=self.include_smart_subtitle,
        )


class RenderPayload(BaseModel):
    scene_id: int
    provider: str
    prompt: str
    aspect_ratio: str = "9:16"
    duration: int = 3
    model: Optional[str] = None
    camera: Optional[str] = None
    motion: Optional[str] = None
    lighting: Optional[str] = None
    voiceover: Optional[str] = None


class AudioTrack(BaseModel):
    scene_id: int
    narration_text: Optional[str] = None
    narration_job_id: Optional[str] = None
    voiceover: Optional[str] = None


class RenderArtifacts(BaseModel):
    final_video_url: Optional[str] = None
    output_url: Optional[str] = None
    artifact_id: Optional[str] = None
    artifacts_manifest: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class RenderExecuteResponse(BaseModel):
    render_execute_id: str
    status: str
    orchestration_status: str = "not_orchestrated"
    execution_mode: str = "dry_run"
    degraded: bool = False
    degradation_reasons: List[str] = Field(default_factory=list)
    render_package: Dict[str, Any]
    phases: Dict[str, Any] = Field(default_factory=dict)
    artifacts: RenderArtifacts = Field(default_factory=RenderArtifacts)
    provider_payloads: List[RenderPayload] = Field(default_factory=list)
    audio_tracks: List[AudioTrack] = Field(default_factory=list)
    scenes: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = ""
    error: Optional[str] = None

    model_config = {"extra": "allow"}


# Legacy nested request model kept for backward compatibility.
class RenderPackageRequest(BaseModel):
    storyboard_request: PosterInput
    providers: List[str] = Field(default_factory=lambda: ["veo", "runway", "kling", "seedance2"])
    aspect_ratio: str = "9:16"
    render_mode: str = "provider_ai_video"
    include_audio: bool = True
    include_avatar: bool = True
    include_drama: bool = True
    include_voice_clone: bool = False
    include_smart_subtitle: bool = True


def _build_package_from_legacy(req: RenderPackageRequest) -> Dict[str, Any]:
    bridge = StoryboardToRenderBridge()
    return bridge.build_render_package(
        req.storyboard_request,
        RenderHandoffOptions(
            providers=req.providers,
            aspect_ratio=req.aspect_ratio,
            render_mode=req.render_mode,
            include_audio=req.include_audio,
            include_avatar=req.include_avatar,
            include_drama=req.include_drama,
            include_voice_clone=req.include_voice_clone,
            include_smart_subtitle=req.include_smart_subtitle,
        ),
    )


def _extract_scenes(render_package: Dict[str, Any]) -> List[Dict[str, Any]]:
    selected_storyboard = render_package.get("selected_storyboard", {})
    if isinstance(selected_storyboard, dict):
        scenes = selected_storyboard.get("scenes")
        if isinstance(scenes, list):
            return scenes

    storyboard_response = render_package.get("storyboard_response", {})
    if isinstance(storyboard_response, dict):
        storyboards = storyboard_response.get("storyboards")
        if isinstance(storyboards, list) and storyboards:
            first = storyboards[0]
            if isinstance(first, dict) and isinstance(first.get("scenes"), list):
                return first["scenes"]

    if isinstance(render_package.get("scenes"), list):
        return render_package["scenes"]

    return []


def _open_execute_session():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return db
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Render execution requires a live database session. "
                "Use execution_mode='dry_run' for planning-only responses or restore DB connectivity."
            ),
        ) from exc


def _collect_degradation_reasons(orchestration_result: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    for phase_name, phase_result in (orchestration_result.get("phases") or {}).items():
        if not isinstance(phase_result, dict) or not phase_result.get("degraded"):
            continue
        reason = str(phase_result.get("degradation_reason") or "").strip()
        reasons.append(reason or f"{phase_name} returned degraded output.")
    return reasons


def _resolve_response_status(
    *,
    execution_mode: str,
    orchestration_status: str,
    degraded: bool,
) -> str:
    if orchestration_status in {"failed", "partial_failure"}:
        return "failed"
    if degraded:
        return "degraded"
    if execution_mode == "execute":
        return "executed"
    return "dry_run"


@router.post("/render-package")
def build_render_package(req: RenderPackageRequest | PosterVideoRenderRequest):
    if isinstance(req, PosterVideoRenderRequest):
        bridge = StoryboardToRenderBridge()
        return bridge.build_render_package(req.to_poster_input(), req.to_handoff_options())
    return _build_package_from_legacy(req)


@router.post("/render-package-v2")
def build_render_package_v2(req: PosterVideoRenderRequest):
    bridge = StoryboardToRenderBridge()
    return bridge.build_render_package(req.to_poster_input(), req.to_handoff_options())


@router.post("/render-execute", response_model=RenderExecuteResponse)
def execute_full_render_pipeline(req: PosterVideoRenderRequest) -> RenderExecuteResponse:
    bridge = StoryboardToRenderBridge()
    render_package = bridge.build_render_package(req.to_poster_input(), req.to_handoff_options())

    orchestrator = RenderOrchestrator()
    if req.execution_mode == "execute":
        with closing(_open_execute_session()) as db_session:
            orchestration_result = orchestrator.orchestrate(render_package, db_session=db_session)
    else:
        orchestration_result = orchestrator.orchestrate(render_package, db_session=None)

    degradation_reasons = _collect_degradation_reasons(orchestration_result)

    orchestration_status = str(orchestration_result.get("status", "unknown"))
    response_status = _resolve_response_status(
        execution_mode=req.execution_mode,
        orchestration_status=orchestration_status,
        degraded=bool(degradation_reasons),
    )

    response = RenderExecuteResponse(
        render_execute_id=orchestration_result.get("orchestration_id", ""),
        status=response_status,
        orchestration_status=orchestration_status,
        execution_mode=req.execution_mode,
        degraded=bool(degradation_reasons),
        degradation_reasons=degradation_reasons,
        render_package=render_package,
        phases=orchestration_result.get("phases", {}),
        timestamp=orchestration_result.get("timestamp", ""),
        error=orchestration_result.get("error"),
    )

    response.scenes = _extract_scenes(render_package)

    render_handoff = render_package.get("render_handoff", {})
    for payload in render_handoff.get("payloads", []):
        if not isinstance(payload, dict):
            continue
        response.provider_payloads.append(
            RenderPayload(
                scene_id=int(payload.get("scene_id") or 0),
                provider=str(payload.get("provider") or ""),
                prompt=str(payload.get("prompt") or ""),
                aspect_ratio=str(payload.get("aspect_ratio") or "9:16"),
                duration=int(payload.get("duration") or 3),
                model=payload.get("model"),
                camera=payload.get("camera"),
                motion=payload.get("motion"),
                lighting=payload.get("lighting"),
                voiceover=payload.get("voiceover"),
            )
        )

    audio_plan = render_package.get("audio_plan", {})
    for track in audio_plan.get("tracks", []):
        if not isinstance(track, dict):
            continue
        narration_job_id_raw = track.get("narration_job_id")
        response.audio_tracks.append(
            AudioTrack(
                scene_id=int(track.get("scene_id") or 0),
                narration_text=track.get("narration_text"),
                narration_job_id=(str(narration_job_id_raw) if narration_job_id_raw is not None else None),
                voiceover=track.get("voiceover"),
            )
        )

    phase_3 = orchestration_result.get("phases", {}).get("phase_3", {})
    if isinstance(phase_3, dict):
        response.artifacts.output_url = phase_3.get("output_url")
        if phase_3.get("output_url"):
            response.artifacts.final_video_url = phase_3.get("output_url")

    response.artifacts.artifact_id = orchestration_result.get("orchestration_id")

    if isinstance(orchestration_result.get("artifacts"), dict):
        response.artifacts.artifacts_manifest = orchestration_result.get("artifacts")

    return response
