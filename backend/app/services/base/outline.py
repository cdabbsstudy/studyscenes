from abc import ABC, abstractmethod

from app.schemas.generation import OutlineResponse


class OutlineServiceBase(ABC):
    @abstractmethod
    async def generate(self, content: str) -> OutlineResponse:
        ...
