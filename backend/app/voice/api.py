from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.voice.contracts import GenerateLineJobRequest, TimelineMixRequest, TimelineMixResponse, VoiceProfileRequest
from app.voice.job_store import JSONJobStore
from app.voice.queue import VoiceQueue
from app.voice.timeline_mix import RealVoiceTimelineMixService
from app.voice.worker_client import HybridVoiceWorkerClient

router = APIRouter(tags=["hybrid-voice-indextts2-supertonic"])
queue = VoiceQueue()
store = JSONJobStore()


@router.post("/voice/jobs")
def enqueue_job(payload: GenerateLineJobRequest, background_tasks: BackgroundTasks):
    return queue.enqueue(payload, background_tasks)


@router.get("/voice/jobs/{job_id}")
def get_job(job_id: str):
    try:
        return store.get(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")


@router.get("/voice/jobs")
def list_jobs():
    return {"items": store.all()}


@router.post("/voice/profile/build")
async def build_voice_profile(payload: VoiceProfileRequest):
    return await HybridVoiceWorkerClient().build_profile(payload)


@router.get("/voice/worker/health")
async def worker_health():
    return await HybridVoiceWorkerClient().health()


@router.post("/voice/timeline/mix", response_model=TimelineMixResponse)
def mix_timeline(payload: TimelineMixRequest):
    return RealVoiceTimelineMixService().mix(payload)
