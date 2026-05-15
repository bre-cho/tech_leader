from fastapi import APIRouter

from app.tts_studio.contracts import (
    ExportMixRequest,
    GenerateLineRequest,
    StudioRunRequest,
    StudioRunResponse,
    TimelineBuildRequest,
)
from app.tts_studio.export_mix import ExportMixService
from app.tts_studio.indextts_provider import IndexTTSProviderBoundary
from app.tts_studio.studio_orchestrator import IndexTTSWorkflowStudioOrchestrator
from app.tts_studio.timeline import TimelineBuilder

router = APIRouter(tags=["indextts-workflow-studio"])


@router.post("/tts-studio/run", response_model=StudioRunResponse)
def run_tts_studio(payload: StudioRunRequest):
    return IndexTTSWorkflowStudioOrchestrator().run(payload)


@router.post("/tts-studio/generate-line")
def generate_line(payload: GenerateLineRequest):
    return IndexTTSProviderBoundary().generate_line(payload, output_dir="/tmp/indextts-line")


@router.post("/tts-studio/timeline/build")
def build_timeline(payload: TimelineBuildRequest):
    return TimelineBuilder().build(payload)


@router.post("/tts-studio/export-mix")
def export_mix(payload: ExportMixRequest):
    return {"output_path": ExportMixService().export(payload)}
