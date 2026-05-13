from fastapi import APIRouter
from app.runtime.lipdub_contracts import CreativeLipDubWorkflowRequest, CreativeLipDubWorkflowResponse
from app.runtime.creative_lipdub_workflow import CreativeLipDubWorkflow
router=APIRouter(tags=['creative-execution-graph'])
@router.post('/creative-execution/lipdub-workflow', response_model=CreativeLipDubWorkflowResponse)
def run_creative_lipdub_workflow(payload: CreativeLipDubWorkflowRequest): return CreativeLipDubWorkflow().run(payload)
