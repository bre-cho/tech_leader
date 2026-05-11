from __future__ import annotations

from typing import Any

from app.render.assembly.schemas.assembly_request import AssemblyRequest


class AssemblyService:
    def assemble(self, payload: AssemblyRequest | dict[str, Any]) -> dict[str, Any]:
        request = payload if isinstance(payload, AssemblyRequest) else AssemblyRequest.model_validate(payload)
        return {
            "status": "assembled",
            "project_id": request.project_id,
            "episode_id": request.episode_id,
            "assembly_plan": request.assembly_plan,
        }
