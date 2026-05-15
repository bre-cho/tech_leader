from __future__ import annotations

import os
import httpx
from app.indextts.contracts import GenerateLineJobRequest


class IndexTTSWorkerClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("INDEXTTS_WORKER_URL", "http://localhost:8091")).rstrip("/")

    async def health(self):
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/health")
            r.raise_for_status()
            return r.json()

    async def generate_line(self, job_id: str, req: GenerateLineJobRequest):
        payload = {
            "job_id": job_id,
            **req.model_dump(),
        }
        async with httpx.AsyncClient(timeout=1800) as client:
            r = await client.post(f"{self.base_url}/generate-line", json=payload)
            r.raise_for_status()
            return r.json()
