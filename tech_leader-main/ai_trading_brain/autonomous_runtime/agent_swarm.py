from __future__ import annotations
from .models import AgentTask

class AgentSwarmPlanner:
    def plan(self, goal: str) -> list[AgentTask]:
        return [
            AgentTask("task_research", "research_agent", f"Thu thập ngữ cảnh cho: {goal}"),
            AgentTask("task_architecture", "architect_agent", f"Thiết kế giải pháp cho: {goal}"),
            AgentTask("task_execution", "builder_agent", f"Thực thi bản nâng cấp cho: {goal}"),
            AgentTask("task_verification", "qa_agent", f"Kiểm thử và chặn lỗi cho: {goal}"),
        ]
