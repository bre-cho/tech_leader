import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.creative_os.provider_duration_profiles import PROVIDER_DURATION_PROFILES
from app.creative_os.safe_render_queue import safe_render_queue
from app.creative_os.scene_count_planner import plan_storyboard
from app.creative_os.schemas import StoryboardPlanRequest

router = APIRouter(prefix="/creative-os", tags=["creative-os"])
EVENTS: dict[str, list[dict]] = {}


@router.get("/provider-profiles")
def get_provider_profiles():
    return PROVIDER_DURATION_PROFILES


@router.post("/projects/{project_id}/plan-storyboard")
def create_storyboard_plan(project_id: str, payload: StoryboardPlanRequest):
    try:
        plan = plan_storyboard(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    EVENTS.setdefault(project_id, []).append(
        {
            "message": (
                f"Storyboard planned: {plan.scene_count} scenes, "
                f"{plan.total_batches} batches, concurrency=1."
            ),
            "payload": plan.model_dump(mode="json"),
        }
    )
    return plan


@router.get("/projects/{project_id}/render-steps")
def get_render_steps(project_id: str, scene_count: int, planned_batch_size: int = 6):
    del project_id

    fake_plan = type("Plan", (), {})()
    fake_plan.batches = []
    start = 1
    batch_index = 1

    while start <= scene_count:
        end = min(start + planned_batch_size - 1, scene_count)
        fake_plan.batches.append(
            type(
                "Batch",
                (),
                {
                    "batch_index": batch_index,
                    "scene_indexes": list(range(start, end + 1)),
                },
            )()
        )
        start = end + 1
        batch_index += 1

    return safe_render_queue.build_execution_steps(fake_plan)


@router.get("/projects/{project_id}/events")
async def stream_project_events(project_id: str):
    async def event_generator():
        sent = 0
        while sent < 60:
            events = EVENTS.get(project_id, [])
            for event in events[sent:]:
                yield f"data: {json.dumps(event)}\\n\\n"
                sent += 1
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
