from fastapi import APIRouter
from app.visual_fashion_runtime.schemas import FashionRuntimeRequest
from app.visual_fashion_runtime.orchestrator import fashion_beauty_runtime_orchestrator

router = APIRouter(prefix="/fashion-runtime", tags=["fashion-runtime"])


@router.post("/analyze")
def analyze_fashion_runtime(payload: FashionRuntimeRequest):
    return fashion_beauty_runtime_orchestrator.analyze(payload)


@router.post("/generate-storyboard")
def generate_storyboard(payload: FashionRuntimeRequest):
    response = fashion_beauty_runtime_orchestrator.analyze(payload)
    return {
        "project_id": response.project_id,
        "storyboard": response.storyboard,
        "sequential_render_plan": response.sequential_render_plan,
        "winner_dna_memory": response.winner_dna_memory,
    }


@router.get("/taxonomy")
def taxonomy():
    return {
        "archetypes": [
            "quiet_luxury_kbeauty_editorial",
            "hyper_feminine_pastel_fashion_motion",
            "cinematic_kbeauty_fashion_commerce",
        ],
        "core_engines": [
            "visual_dna_extractor",
            "emotional_perception_graph",
            "character_continuity_runtime",
            "fashion_motion_engine",
            "beauty_commerce_engine",
            "storyboard_runtime",
            "winner_dna_memory",
        ],
        "render_policy": {
            "planned_batch_size": "configurable",
            "max_concurrent_render": 1,
            "execution_mode": "sequential",
        },
    }
