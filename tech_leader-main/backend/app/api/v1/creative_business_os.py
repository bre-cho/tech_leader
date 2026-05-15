from fastapi import APIRouter
from app.core.contracts import CreativeOSRequest, CreativeOSResponse
from app.workflows.creative_business_os import CreativeBusinessOSWorkflow

router = APIRouter(tags=["creative-business-os"])

@router.post("/creative-business-os/run", response_model=CreativeOSResponse)
def run_creative_business_os(payload: CreativeOSRequest):
    return CreativeBusinessOSWorkflow().run(payload)
