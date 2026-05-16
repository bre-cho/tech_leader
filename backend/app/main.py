import os
from pathlib import Path

# Load backend/.env before any module reads os.environ.
# This file contains secrets (SEEDANCE_API_KEY etc.) and is gitignored.
# NEVER put these values in Next.js .env.local or Vite frontend/.env.
_backend_env = Path(__file__).resolve().parent.parent / ".env"
if _backend_env.is_file():
    for _line in _backend_env.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

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
from app.creative_os_mvp.api.v1.creative_os import router as creative_os_mvp_router
from app.api.v1.creative_os import router as creative_os_router
from app.api.v1.seedance import router as seedance_router
from app.creative_infra_mvp.api.routes import router as creative_infra_mvp_router
from app.compound_os_mvp.api import router as compound_os_mvp_router
from app.compound_os_mvp.db import init_db as init_compound_os_db

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
app.include_router(creative_os_mvp_router, prefix="/api/v1/creative-os")
app.include_router(creative_os_router, prefix="/api/v1")
app.include_router(seedance_router, prefix="/api/v1")
app.include_router(creative_infra_mvp_router, prefix="/api/v1")
app.include_router(compound_os_mvp_router, prefix="/api/v1/compound-os")
