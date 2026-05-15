from abc import ABC, abstractmethod
from typing import Any

class AgentResult(dict):
    pass

class BaseAgent(ABC):
    name: str = "base-agent"
    required_inputs: list[str] = []
    output_contract: list[str] = []

    def run(self, context: dict[str, Any]) -> AgentResult:
        missing = [k for k in self.required_inputs if k not in context]
        if missing:
            return AgentResult({"agent": self.name, "status": "failed", "error": f"Missing inputs: {missing}"})
        output = self.execute(context)
        return AgentResult({"agent": self.name, "status": "succeeded", "output": output})

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> Any:
        raise NotImplementedError
