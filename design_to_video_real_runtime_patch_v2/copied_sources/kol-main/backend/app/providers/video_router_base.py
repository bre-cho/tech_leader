from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Set


@dataclass(frozen=True)
class ProviderCapability:
    name: str
    modes: Set[str]
    enabled: bool
    priority: int = 100
    cost_score: float = 0.5
    latency_score: float = 0.5
    quality_score: float = 0.5


class VideoProvider(ABC):
    """Base contract for synchronous legacy video providers.

    Implementations must provide capability metadata, health status, task
    creation, and task status lookup.
    """

    name: str

    @abstractmethod
    def capability(self) -> ProviderCapability:
        """Return static capability metadata for routing/scoring."""
        raise NotImplementedError

    @abstractmethod
    def healthcheck(self) -> bool:
        """Return ``True`` when provider is currently healthy/reachable."""
        raise NotImplementedError

    @abstractmethod
    def create_task(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Create a provider task and return normalized provider response."""
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> dict[str, Any]:
        """Fetch task status/details from the provider by task id."""
        raise NotImplementedError
