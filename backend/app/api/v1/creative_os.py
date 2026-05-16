from pydantic import BaseModel, Field
from fastapi import APIRouter
from app.creative_os.provider_duration_profiles import PROVIDER_DURATION_PROFILES
from app.creative_os.schemas import StoryboardPlanRequest
from app.creative_os.scene_count_planner import plan_storyboard
from app.creative_os.safe_render_queue import safe_render_queue

router = APIRouter(prefix="/creative-os", tags=["creative-os"])
EVENTS = {}


def _friendly_provider_label(provider: str) -> str:
    key = provider.lower().strip()
    if key in {"seedance2-fast", "seedance2", "seedance"}:
        return "Seedance Fast MVP" if key in {"seedance2-fast", "seedance2"} else "Seedance"
    return provider.replace("_", " ").title()


class RenderExecutionRequest(BaseModel):
    scene_count: int = Field(gt=0)
    planned_batch_size: int = Field(default=6, gt=0)
    provider: str
    image_url: str | None = None

@router.get("/provider-profiles")
def get_provider_profiles():
    return PROVIDER_DURATION_PROFILES

@router.post("/projects/{project_id}/plan-storyboard")
def create_storyboard_plan(project_id: str, payload: StoryboardPlanRequest):
    plan = plan_storyboard(project_id, payload)
    EVENTS.setdefault(project_id, []).append({
        "message": f"Storyboard planned: {plan.scene_count} scenes, {plan.total_batches} batches, concurrency=1, provider={_friendly_provider_label(plan.provider)}.",
        "payload": plan.model_dump(mode="json"),
    })
    return plan

@router.get("/projects/{project_id}/render-steps")
def get_render_steps(project_id: str, scene_count: int, planned_batch_size: int = 6):
    return safe_render_queue.build_execution_steps(scene_count, planned_batch_size, project_id=project_id)


@router.post("/projects/{project_id}/execute-render")
def execute_render(project_id: str, payload: RenderExecutionRequest):
    EVENTS.setdefault(project_id, [])

    def emit(message: str):
        EVENTS[project_id].append({"message": message})

    snapshot = safe_render_queue.start_execution(
        project_id=project_id,
        scene_count=payload.scene_count,
        planned_batch_size=payload.planned_batch_size,
        provider=payload.provider,
        image_url=payload.image_url,
        on_event=emit,
    )
    return snapshot


@router.get("/projects/{project_id}/render-status")
def get_render_status(project_id: str):
    status = safe_render_queue.get_status(project_id)
    return status or {
        "project_id": project_id,
        "status": "idle",
        "steps": [],
        "execution_mode": "sequential",
        "max_concurrent_render": 1,
    }

@router.get("/projects/{project_id}/events")
def get_project_events(project_id: str):
    """Return all events for a project (non-streaming to avoid timeout)."""
    return EVENTS.get(project_id, [])
