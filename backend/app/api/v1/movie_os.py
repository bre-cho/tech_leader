from fastapi import APIRouter
from app.movie_os.schemas import MovieDirectorRequest
from app.movie_os.movie_director_orchestrator import movie_director_orchestrator

router = APIRouter(prefix="/movie-os", tags=["movie-os"])


@router.post("/direct")
def direct_movie(payload: MovieDirectorRequest):
    return movie_director_orchestrator.direct(payload)


@router.get("/health")
def health():
    return {"status": "ok", "module": "movie-os-v3"}
