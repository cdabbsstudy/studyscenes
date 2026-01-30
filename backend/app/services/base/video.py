from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SceneInput:
    image_path: Path
    title: str
    duration_sec: float


class VideoServiceBase(ABC):
    @abstractmethod
    async def stitch(
        self,
        scenes: list[SceneInput],
        audio_path: Path,
        output_path: Path,
    ) -> None:
        """Stitch scene images + single audio track into an MP4 video."""
        ...
