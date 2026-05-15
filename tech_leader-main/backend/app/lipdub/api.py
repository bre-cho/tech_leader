from fastapi import APIRouter
from app.lipdub.contracts import LipDubRequest, LipDubResponse
from app.lipdub.service import LTXLipDubRuntimeService
router=APIRouter(tags=['ltx-lipdub-runtime'])
@router.post('/lipdub/ltx/run', response_model=LipDubResponse)
def run_ltx_lipdub(payload: LipDubRequest): return LTXLipDubRuntimeService().run(payload)
