"""Product ingestion schema stub."""
from typing import Optional
from pydantic import BaseModel


class NormalizedProductProfile(BaseModel):
    product_id: str
    product_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    metadata: Optional[dict] = None


class ProductIngestionRequest(BaseModel):
    product_id: str
    product_name: str
    metadata: dict = None


class ProductIngestionResponse(BaseModel):
    ok: bool = True
    product_id: str
    status: str = "ingested"
