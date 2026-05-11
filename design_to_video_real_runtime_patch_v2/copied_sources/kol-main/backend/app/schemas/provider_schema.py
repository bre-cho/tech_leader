from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ProviderName(str, Enum):
    youtube = "youtube"
    veo = "veo"
    thumbnail = "thumbnail"
    simulated = "simulated"
    volcengine = "volcengine"


class ProviderStatus(BaseModel):
    provider: ProviderName
    enabled: bool
    configured: bool
    dry_run_default: bool = True
    message: str = ""


class ProviderOperationRequest(BaseModel):
    provider: ProviderName
    operation: str = Field(min_length=1)
    input: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = True


class ProviderPayloadPreview(BaseModel):
    provider: ProviderName
    operation: str
    payload: Dict[str, Any]
    dry_run: bool = True


class ProviderExecutionResult(BaseModel):
    provider: ProviderName
    operation: str
    dry_run: bool
    accepted: bool
    external_job_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class ProviderCallbackResult(BaseModel):
    provider: ProviderName
    accepted: bool
    event_type: str = "provider_callback"
    external_job_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""
