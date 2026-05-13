from fastapi import APIRouter
from apps.api.schemas.fashion_poster import FashionPosterInput, FashionPosterResponse
from packages.fashion_poster_factory import FashionPosterFactoryService


router = APIRouter(prefix="/api/v1/fashion-poster-factory", tags=["Fashion Poster Factory"])
factory = FashionPosterFactoryService()


@router.post("/generate", response_model=FashionPosterResponse)
def generate_fashion_poster(payload: FashionPosterInput):
    return factory.generate(payload.model_dump())


@router.post("/batch", response_model=list[FashionPosterResponse])
def batch_generate(payloads: list[FashionPosterInput]):
    return factory.batch_generate([p.model_dump() for p in payloads])
