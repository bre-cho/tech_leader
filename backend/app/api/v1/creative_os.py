import asyncio, json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.creative_os.provider_duration_profiles import PROVIDER_DURATION_PROFILES
from app.creative_os.schemas import StoryboardPlanRequest
from app.creative_os.scene_count_planner import plan_storyboard
from app.creative_os.safe_render_queue import safe_render_queue

router = APIRouter(prefix="/creative-os", tags=["creative-os"])
EVENTS = {}

@router.get("/provider-profiles")
def get_provider_profiles():
    return PROVIDER_DURATION_PROFILES

@router.post("/projects/{project_id}/plan-storyboard")
def create_storyboard_plan(project_id: str, payload: StoryboardPlanRequest):
    plan = plan_storyboard(project_id, payload)
    EVENTS.setdefault(project_id, []).append({
        "message": f"Storyboard planned: {plan.scene_count} scenes, {plan.total_batches} batches, concurrency=1.",
        "payload": plan.model_dump(mode="json"),
    })
    return plan

@router.get("/projects/{project_id}/render-steps")
def get_render_steps(project_id: str, scene_count: int, planned_batch_size: int = 6):
    return safe_render_queue.build_execution_steps(scene_count, planned_batch_size)

@router.get("/projects/{project_id}/events")
def get_project_events(project_id: str):
    """Return all events for a project (non-streaming to avoid timeout)."""
    return EVENTS.get(project_id, [])
