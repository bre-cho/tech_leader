from fastapi import APIRouter
from typing import Any, Dict

from ._utils import require_project_and_trace, standard_response

router = APIRouter(prefix="/crm", tags=["crm"])


@router.post("/followup")
def create_followup(payload: Dict[str, Any]):
    project_id, trace_id = require_project_and_trace(payload)
    data = {
        "sequence": [
            {"delay": "10_minutes", "message": "Gợi ý video 15s từ ảnh vừa thiết kế."},
            {"delay": "24_hours", "message": "Cho khách xem demo motion concept."},
            {"delay": "3_days", "message": "Đề xuất combo tiết kiệm."},
            {"delay": "7_days", "message": "Gợi ý campaign mới."},
        ]
    }
    return standard_response(
        project_id=project_id,
        trace_id=trace_id,
        data=data,
        step="crm.followup.scheduled",
    )
