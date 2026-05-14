from __future__ import annotations
import hashlib, math, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from app.memory.contracts import MemoryCreateRequest, MemoryRecord, MemorySearchRequest, MemorySearchResult, RecallContextRequest, RecallContextResponse

def now_iso(): return datetime.now(timezone.utc).isoformat()
def stable_id(v: str): return 'mem_' + hashlib.sha256(v.encode()).hexdigest()[:16]
def tokenize(t: str): return re.findall(r"[\wÀ-ỹ]+", t.lower())
def embed_text(text: str, dims: int=128):
    vec=[0.0]*dims
    for tok in tokenize(text):
        h=int(hashlib.sha256(tok.encode()).hexdigest(),16)
        vec[h%dims]+= 1.0 if ((h>>8)%2==0) else -1.0
    norm=math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x/norm for x in vec]
def cosine(a,b): return sum(x*y for x,y in zip(a,b))

class LocalSecondBrainStore:
    # Local fallback. Production mapping: JSONL=>Cloudflare D1, embed_text=>Workers AI, cosine scan=>Vectorize.
    def __init__(self, path: str='storage/second_brain_memory.jsonl'):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def create(self, payload: MemoryCreateRequest) -> MemoryRecord:
        stamp=now_iso(); raw=f"{payload.namespace}:{payload.kind}:{payload.title}:{payload.content}"
        rec=MemoryRecord(
            id=stable_id(raw), kind=payload.kind, namespace=payload.namespace,
            title=payload.title, content=payload.content, tags=payload.tags,
            metadata=payload.metadata,
            embedding=embed_text(payload.title+'\n'+payload.content+'\n'+' '.join(payload.tags)),
            layer=payload.layer, version=payload.version, source_agent_id=payload.source_agent_id,
            created_at=stamp, updated_at=stamp,
        )
        records={r.id:r for r in self.all()}; records[rec.id]=rec; self._write(records.values()); return rec
    def all(self):
        if not self.path.exists(): return []
        return [MemoryRecord.model_validate_json(line) for line in self.path.read_text(encoding='utf-8').splitlines() if line.strip()]
    def search(self, payload: MemorySearchRequest):
        q=embed_text(payload.query); out=[]
        for rec in self.all():
            if rec.namespace!=payload.namespace: continue
            if payload.kind and rec.kind!=payload.kind: continue
            if payload.tags and not set(payload.tags).issubset(set(rec.tags)): continue
            score=cosine(q, rec.embedding or embed_text(rec.content))
            if payload.query.lower() in rec.content.lower() or payload.query.lower() in rec.title.lower(): score+=0.25
            out.append(MemorySearchResult(record=rec, score=round(float(score),4)))
        out.sort(key=lambda x:x.score, reverse=True); return out[:payload.limit]

    def search_by_layer(self, layer: str, namespace: str = "default") -> list:
        return [r for r in self.all() if r.layer == layer and r.namespace == namespace]
    def recall_context(self, payload: RecallContextRequest):
        query=' '.join([x for x in [payload.brand_name,payload.avatar_id,payload.campaign_id,payload.product_name,payload.objective] if x])
        results=self.search(MemorySearchRequest(query=query, namespace=payload.namespace, limit=payload.limit))
        lines=['RECALLED SECOND BRAIN CONTEXT:']+[f"{i}. [{r.record.kind}] {r.record.title}: {r.record.content[:500]}" for i,r in enumerate(results,1)]
        return RecallContextResponse(prompt_context='\n'.join(lines), memories=results)
    def _write(self, records: Iterable[MemoryRecord]):
        self.path.write_text('\n'.join([r.model_dump_json() for r in records])+'\n', encoding='utf-8')
