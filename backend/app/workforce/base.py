from __future__ import annotations

from abc import ABC, abstractmethod
from app.workforce.contracts import WorkforceContext, AgentResult, AgentStatus


class WorkforceAgent(ABC):
    name: str = "WorkforceAgent"

    @abstractmethod
    def run(self, context: WorkforceContext) -> AgentResult:
        raise NotImplementedError

    def ok(self, output, confidence=0.85, warnings=None):
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.completed,
            confidence=confidence,
            output=output,
            warnings=warnings or [],
        )
