from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MemoryCreateRequest(BaseModel):
    kind: str
    namespace: str = "default"
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemoryRecord(BaseModel):
    id: str
    kind: str
    namespace: str
    title: str
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: str
    updated_at: str

class MemorySearchRequest(BaseModel):
    query: str
    namespace: str = "default"
    kind: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    limit: int = 8

class MemorySearchResult(BaseModel):
    record: MemoryRecord
    score: float

class MemorySearchResponse(BaseModel):
    items: List[MemorySearchResult]

class RecallContextRequest(BaseModel):
    brand_name: Optional[str] = None
    avatar_id: Optional[str] = None
    campaign_id: Optional[str] = None
    product_name: Optional[str] = None
    objective: str = "lipdub_video"
    namespace: str = "default"
    limit: int = 10

class RecallContextResponse(BaseModel):
    prompt_context: str
    memories: List[MemorySearchResult]
