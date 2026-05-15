from fastapi import APIRouter

from app.video_postprocess.contracts import (
    AudioMixRequest,
    SmartSubtitleRequest,
    SmartSubtitleResponse,
    VideoPostprocessRequest,
    VideoPostprocessResponse,
)
from app.video_postprocess.audio_mix_service import RealAudioMixService
from app.video_postprocess.postprocess_orchestrator import VideoPostprocessOrchestrator
from app.video_postprocess.smart_karaoke_subtitle_service import SmartKaraokeSubtitleService

router = APIRouter(tags=["video-postprocess"])


@router.post("/subtitle/karaoke/build", response_model=SmartSubtitleResponse)
def build_karaoke_subtitles(payload: SmartSubtitleRequest):
    return SmartKaraokeSubtitleService().build(payload)


@router.post("/audio/mix")
def mix_audio(payload: AudioMixRequest):
    path = RealAudioMixService().mix(**payload.model_dump())
    return {"status": "succeeded", "mixed_audio_path": path}


@router.post("/video/postprocess/render", response_model=VideoPostprocessResponse)
def postprocess_video(payload: VideoPostprocessRequest):
    return VideoPostprocessOrchestrator().run(payload)
