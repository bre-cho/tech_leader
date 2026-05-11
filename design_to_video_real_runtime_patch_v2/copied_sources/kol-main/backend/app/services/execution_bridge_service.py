from __future__ import annotations

from typing import Any


class ExecutionBridgeService:
    """Compatibility bridge that normalizes render execution context/payloads."""

    def resolve_context(
        self,
        _db: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, dict):
                context[key] = dict(value)
            else:
                context[key] = value
        return context

    def transform_scene_payload(
        self,
        scene_payload: dict[str, Any],
        bridge_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(scene_payload or {})
        if not bridge_context:
            return payload

        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        metadata.setdefault("execution_bridge_context", {})
        metadata["execution_bridge_context"].update(bridge_context)
        payload["metadata"] = metadata
        return payload

    def resolve_project_context(self, db: Any, project: dict[str, Any]) -> dict[str, Any]:
        context = self.resolve_context(
            db,
            project_id=project.get("id"),
            avatar_id=project.get("avatar_id"),
            market_code=project.get("market_code"),
            content_goal=project.get("goal") or project.get("content_goal"),
            conversion_mode=project.get("conversion_mode"),
            project_metadata=project.get("metadata") if isinstance(project.get("metadata"), dict) else None,
        )
        return context

    def apply_to_project_scene(
        self,
        scene: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.transform_scene_payload(scene, execution_context or {})
