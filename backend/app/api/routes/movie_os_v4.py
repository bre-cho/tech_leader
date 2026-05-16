from fastapi import APIRouter
from app.movie_os_v4.schemas import MovieOSV4Request, SceneRebuildRequest
from app.movie_os_v4.autonomous_movie_orchestrator import autonomous_movie_orchestrator
from app.movie_os_v4.scene_dependency_rebuilder import scene_dependency_rebuilder

router = APIRouter(prefix="/movie-os-v4", tags=["movie-os-v4"])


@router.post("/direct")
def direct_movie(payload: MovieOSV4Request):
    return autonomous_movie_orchestrator.direct(payload)


@router.post("/rebuild-scene")
def rebuild_scene(payload: SceneRebuildRequest):
    return scene_dependency_rebuilder.plan_rebuild(payload)


@router.get("/taxonomy")
def taxonomy():
    return {
        "moods": [
            "gothic_luxury",
            "vogue_fantasy",
            "ethereal_spiritual",
            "cinematic_fantasy",
        ],
        "camera_language": [
            "slow cinematic push-in",
            "controlled portrait glide",
            "wide crane reveal",
            "macro beauty detail",
            "handheld emotional drift",
            "orbit transformation move",
            "dolly with fabric motion",
            "rising hero orbit",
            "final locked tableau",
        ],
        "runtime_policy": {
            "planned_batch_size": "configurable",
            "max_concurrent_render": 1,
            "execution_mode": "sequential",
        },
    }
