import json, os, time
from typing import Dict, Any

MEMORY_PATH = os.getenv("CREATIVE_MEMORY_PATH", "/tmp/creative_infrastructure_memory.jsonl")

class MemoryStore:
    def append(self, record: Dict[str, Any]) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        record = {**record, "created_at": time.time()}
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"stored": True, "path": MEMORY_PATH, "record_type": record.get("type")}

class WinnerDNAEngine:
    def update(self, req: Dict[str, Any], reasoning: Dict[str, Any], gate: Dict[str, Any]) -> Dict[str, Any]:
        candidate = {
            "type": "winner_dna",
            "industry": req["industry"],
            "product_or_service": req["product_or_service"],
            "attention_order": reasoning["attention"]["visual_attention_order"],
            "psychology": reasoning["psychology"],
            "score": reasoning["commercial_reasoning_score"],
            "status": gate["status"],
        }
        if gate["status"] in ["PROMOTED", "CANDIDATE"]:
            MemoryStore().append(candidate)
            candidate["stored"] = True
        else:
            candidate["stored"] = False
        return candidate
