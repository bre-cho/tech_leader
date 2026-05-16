from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as design_router
from app.api.workforce_routes import router as workforce_router
from app.api.routes_infrastructure import router as infrastructure_router
from app.memory.second_brain_api import router as second_brain_router
from app.lipdub.api import router as lipdub_router
from app.runtime.creative_lipdub_api import router as creative_lipdub_router
from app.video_postprocess.api import router as video_postprocess_router
from app.indextts.api import router as indextts_router
from app.voice.api import router as voice_router
from app.tts_studio.api import router as tts_studio_router
from app.api.v1.creative_business_os import router as creative_business_os_router
from app.api.v1.enterprise_memory import router as enterprise_memory_router
from app.api.v1.creative_os import router as creative_os_router
from app.creative_os_mvp.api.v1.creative_os import router as creative_os_mvp_router
from app.creative_infra_mvp.api.routes import router as creative_infra_mvp_router
from app.compound_os_mvp.api import router as compound_os_mvp_router
from app.compound_os_mvp.db import init_db as init_compound_os_db
from app.api.v1.architecture_control_tower import router as architecture_router
from app.api.v1.commercial_intelligence import router as commercial_intelligence_router
from app.api.v1.fashion_beauty_runtime import router as fashion_beauty_router

app = FastAPI(title="Agentic Creative Operating Environment", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_init_databases():
    # Keep compound OS tables available without affecting the main runtime DB setup.
    init_compound_os_db()

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "agentic-creative-operating-environment", "strict_law": True}

app.include_router(design_router, prefix="/api/v1")
app.include_router(workforce_router, prefix="/api/v1")
app.include_router(infrastructure_router, prefix="/api/v1")
app.include_router(second_brain_router, prefix="/api/v1")
app.include_router(lipdub_router, prefix="/api/v1")
app.include_router(creative_lipdub_router, prefix="/api/v1")
app.include_router(video_postprocess_router, prefix="/api/v1")
app.include_router(indextts_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")
app.include_router(tts_studio_router, prefix="/api/v1")
app.include_router(creative_business_os_router, prefix="/api/v1")
app.include_router(enterprise_memory_router, prefix="/api/v1")
app.include_router(creative_os_router, prefix="/api/v1")
app.include_router(creative_os_mvp_router, prefix="/api/v1/creative-os")
app.include_router(creative_infra_mvp_router, prefix="/api/v1")
app.include_router(compound_os_mvp_router, prefix="/api/v1/compound-os")
app.include_router(architecture_router, prefix="/api/v1")
app.include_router(commercial_intelligence_router)
app.include_router(fashion_beauty_router, prefix="/api/v1")
