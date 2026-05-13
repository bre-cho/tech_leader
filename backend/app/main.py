from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as design_router
from app.api.workforce_routes import router as workforce_router

app = FastAPI(title="Agentic Creative Operating Environment", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "agentic-creative-operating-environment", "strict_law": True}

app.include_router(design_router, prefix="/api/v1")
app.include_router(workforce_router, prefix="/api/v1")
