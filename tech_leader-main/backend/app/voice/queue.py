from __future__ import annotations

import asyncio
import uuid
from fastapi import BackgroundTasks
from app.voice.contracts import GenerateLineJobRequest, JobRecord, JobStatus
from app.voice.job_store import JSONJobStore
from app.voice.worker_client import HybridVoiceWorkerClient


class RetryPolicy:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def delay(self, attempt: int) -> float:
        return min(2 ** max(attempt - 1, 0), 30)


class VoiceQueue:
    def __init__(self):
        self.store = JSONJobStore()
        self.client = HybridVoiceWorkerClient()
        self.retry = RetryPolicy()

    def enqueue(self, req: GenerateLineJobRequest, background: BackgroundTasks) -> JobRecord:
        job_id = "voice_" + uuid.uuid4().hex[:12]
        rec = self.store.create(job_id, req)
        background.add_task(self._run_job, job_id)
        return rec

    async def _run_job(self, job_id: str):
        rec = self.store.get(job_id)
        while rec.attempts < rec.max_attempts:
            rec.attempts += 1
            rec.status = JobStatus.running if rec.attempts == 1 else JobStatus.retrying
            rec.error = None
            self.store.update(rec)
            try:
                response = await self.client.generate_line(job_id, rec.request)
                rec.response = response
                rec.status = JobStatus.succeeded
                self.store.update(rec)
                return
            except Exception as e:
                rec.error = str(e)
                rec.status = JobStatus.failed
                self.store.update(rec)
                if rec.attempts >= rec.max_attempts:
                    return
                await asyncio.sleep(self.retry.delay(rec.attempts))
