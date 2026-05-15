from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.indextts.contracts import GenerateLineJobRequest, TimelineMixRequest, TimelineMixResponse
from app.indextts.job_store import JSONJobStore
from app.indextts.queue import IndexTTSQueue
from app.indextts.timeline_mix import RealTimelineMixService
from app.indextts.worker_client import IndexTTSWorkerClient

router = APIRouter(tags=["indextts-real-worker"])
queue = IndexTTSQueue()
store = JSONJobStore()


@router.post("/indextts/jobs")
def enqueue_job(payload: GenerateLineJobRequest, background_tasks: BackgroundTasks):
    return queue.enqueue(payload, background_tasks)


@router.get("/indextts/jobs/{job_id}")
def get_job(job_id: str):
    try:
        return store.get(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")


@router.get("/indextts/jobs")
def list_jobs():
    return {"items": store.all()}


@router.get("/indextts/worker/health")
async def worker_health():
    return await IndexTTSWorkerClient().health()


@router.post("/indextts/timeline/mix", response_model=TimelineMixResponse)
def mix_timeline(payload: TimelineMixRequest):
    return RealTimelineMixService().mix(payload)
