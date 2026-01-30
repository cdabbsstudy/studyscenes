from abc import ABC, abstractmethod
from pathlib import Path


class VoiceServiceBase(ABC):
    @abstractmethod
    async def generate_scene(self, narration: str, output_path: Path) -> float:
        """Generate audio for one scene. Returns duration in seconds."""
        ...
