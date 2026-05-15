import json, time, uuid
from app.creative_os_mvp.core.config import settings

class JsonlMemoryStore:
    def __init__(self, name: str):
        self.path=settings.memory_dir / f"{name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict) -> dict:
        record={"id": str(uuid.uuid4()), "created_at": time.time(), **record}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False)+"\n")
        return record

    def list(self, limit: int=50) -> list[dict]:
        if not self.path.exists(): return []
        rows=[json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]
        return rows[-limit:][::-1]

class WinnerDNAEngine:
    def __init__(self):
        self.store=JsonlMemoryStore("winner_dna")

    def maybe_store(self, req, reasoning, promotion: dict, artifacts: list) -> dict:
        if not promotion.get("approved"):
            return {"stored": False, "reason": promotion.get("reason", "not approved")}
        record=self.store.append({
            "industry": req.brand.industry,
            "brand": req.brand.brand_name,
            "product_type": req.brand.product_type,
            "score": reasoning.total_score,
            "attention_route": reasoning.attention_route,
            "visual_dna": reasoning.category.get("visual_dna", []),
            "artifact_ids": [a.artifact_id for a in artifacts],
        })
        return {"stored": True, "record_id": record["id"]}
