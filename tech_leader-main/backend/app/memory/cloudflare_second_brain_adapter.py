from __future__ import annotations
import os, httpx
from app.memory.contracts import MemoryCreateRequest, MemorySearchRequest

class CloudflareSecondBrainAdapter:
    # Adapter for rahilp/second-brain-cloudflare style Worker deployment.
    def __init__(self, base_url=None, api_key=None):
        self.base_url=(base_url or os.getenv('SECOND_BRAIN_BASE_URL','')).rstrip('/')
        self.api_key=api_key or os.getenv('SECOND_BRAIN_API_KEY','')
    def enabled(self): return bool(self.base_url)
    async def create(self, payload: MemoryCreateRequest):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post(f'{self.base_url}/memory', headers=self._headers(), json=payload.model_dump()); r.raise_for_status(); return r.json()
    async def search(self, payload: MemorySearchRequest):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post(f'{self.base_url}/search', headers=self._headers(), json=payload.model_dump()); r.raise_for_status(); return r.json()
    def _headers(self):
        h={'Content-Type':'application/json'}
        if self.api_key: h['Authorization']=f'Bearer {self.api_key}'
        return h
