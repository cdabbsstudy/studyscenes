from abc import ABC, abstractmethod

from app.schemas.generation import OutlineResponse, ScriptResponse


class ScriptServiceBase(ABC):
    @abstractmethod
    async def generate(self, outline: OutlineResponse) -> ScriptResponse:
        ...
