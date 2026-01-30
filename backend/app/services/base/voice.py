from abc import ABC, abstractmethod
from pathlib import Path

from app.schemas.generation import ScriptResponse


class VoiceServiceBase(ABC):
    @abstractmethod
    async def generate(self, script: ScriptResponse, output_path: Path) -> float:
        """Generate a single narration audio file for the entire script.

        Returns the total duration in seconds.
        """
        ...
