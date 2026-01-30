from abc import ABC, abstractmethod
from pathlib import Path


class ImageServiceBase(ABC):
    @abstractmethod
    async def generate(
        self,
        scene_title: str,
        visual_desc: str,
        output_path: Path,
        *,
        narration: str = "",
        key_points: list[str] | None = None,
    ) -> None:
        """Generate a single scene image."""
        ...
