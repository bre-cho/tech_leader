from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.creative_os_mvp.api.v1.creative_os import router as creative_os_router
from app.creative_os_mvp.api.v1.commercial_intelligence import router as commercial_router
from app.creative_os_mvp.api.v1.memory import router as memory_router
from app.creative_os_mvp.api.v1.artifacts import router as artifacts_router
from app.creative_os_mvp.core.config import settings

app = FastAPI(title="AI-Native Creative Operating System", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(creative_os_router, prefix="/api/v1/creative-os", tags=["Creative OS"])
app.include_router(commercial_router, prefix="/api/v1/commercial-intelligence", tags=["Commercial Intelligence"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(artifacts_router, prefix="/api/v1/artifacts", tags=["Artifacts"])

@app.get("/health")
def health():
    return {"status":"ok", "service":"ai-native-creative-os", "provider": settings.provider}
