from abc import ABC, abstractmethod
from app.creative_os_mvp.models.schemas import CreativeRequest

class RenderProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, negative_prompt: str, req: CreativeRequest) -> bytes:
        raise NotImplementedError
