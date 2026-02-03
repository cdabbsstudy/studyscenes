from abc import ABC, abstractmethod
from pathlib import Path


class VideoClipServiceBase(ABC):
    @abstractmethod
    async def generate(
        self,
        scene_title: str,
        visual_desc: str,
        output_path: Path,
        *,
        narration: str = "",
        duration_sec: int = 6,
    ) -> None:
        """Generate a video clip for a single scene."""
        ...
