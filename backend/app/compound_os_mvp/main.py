from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.compound_os_mvp.api import router
from app.compound_os_mvp.db import init_db

app = FastAPI(
    title="AI-Native Creative Business OS",
    version="1.0.0",
    description="Creative operational intelligence, not a poster generator."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(router, prefix="/api/v1")
