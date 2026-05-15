from fastapi import APIRouter
from app.memory.contracts import MemoryCreateRequest, MemoryRecord, MemorySearchRequest, MemorySearchResponse, RecallContextRequest, RecallContextResponse
from app.memory.local_second_brain import LocalSecondBrainStore
router=APIRouter(tags=['second-brain-memory']); store=LocalSecondBrainStore()
@router.post('/memory/create', response_model=MemoryRecord)
def create_memory(payload: MemoryCreateRequest): return store.create(payload)
@router.post('/memory/search', response_model=MemorySearchResponse)
def search_memory(payload: MemorySearchRequest): return MemorySearchResponse(items=store.search(payload))
@router.post('/memory/recall-context', response_model=RecallContextResponse)
def recall_context(payload: RecallContextRequest): return store.recall_context(payload)
@router.get('/memory/all')
def all_memory(): return {'items': store.all()}
