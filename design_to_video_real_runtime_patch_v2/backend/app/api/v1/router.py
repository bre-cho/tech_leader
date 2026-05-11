from fastapi import APIRouter
from .design import router as design_router
from .upsell import router as upsell_router
from .video import router as video_router
from .offers import router as offers_router
from .crm import router as crm_router
from .memory import router as memory_router
from .dashboard import router as dashboard_router
from .render import router as render_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(design_router)
api_router.include_router(upsell_router)
api_router.include_router(video_router)
api_router.include_router(offers_router)
api_router.include_router(crm_router)
api_router.include_router(memory_router)
api_router.include_router(dashboard_router)
api_router.include_router(render_router)
