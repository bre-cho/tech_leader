from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from app.voice.contracts import GenerateLineJobRequest, JobRecord, JobStatus


def now():
    return datetime.now(timezone.utc).isoformat()


class JSONJobStore:
    def __init__(self, path: str = "storage/voice_jobs.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def create(self, job_id: str, req: GenerateLineJobRequest) -> JobRecord:
        rec = JobRecord(job_id=job_id, status=JobStatus.queued, request=req, created_at=now(), updated_at=now())
        records = {r.job_id: r for r in self.all()}
        records[job_id] = rec
        self._write(records.values())
        return rec

    def update(self, rec: JobRecord) -> JobRecord:
        rec.updated_at = now()
        records = {r.job_id: r for r in self.all()}
        records[rec.job_id] = rec
        self._write(records.values())
        return rec

    def get(self, job_id: str) -> JobRecord:
        for r in self.all():
            if r.job_id == job_id:
                return r
        raise KeyError(job_id)

    def all(self) -> list[JobRecord]:
        if not self.path.exists():
            return []
        return [JobRecord.model_validate_json(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _write(self, records):
        self.path.write_text("\n".join([r.model_dump_json() for r in records]) + "\n", encoding="utf-8")
