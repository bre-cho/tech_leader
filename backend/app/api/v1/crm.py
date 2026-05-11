from fastapi import APIRouter
from typing import Any, Dict

router = APIRouter(prefix="/crm", tags=["crm"])


@router.post("/followup")
def create_followup(payload: Dict[str, Any]):
    project_id = payload.get("project_id")
    return {
        "ok": True,
        "data": {
            "project_id": project_id,
            "sequence": [
                {"delay": "10_minutes", "message": "Gợi ý video 15s từ ảnh vừa thiết kế."},
                {"delay": "24_hours", "message": "Cho khách xem demo motion concept."},
                {"delay": "3_days", "message": "Đề xuất combo tiết kiệm."},
                {"delay": "7_days", "message": "Gợi ý campaign mới."},
            ],
        },
    }
