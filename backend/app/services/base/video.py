from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SceneInput:
    visual_path: Path   # .mp4 (AI clip) or .png (fallback image)
    audio_path: Path
    title: str
    duration_sec: float


class VideoServiceBase(ABC):
    @abstractmethod
    async def stitch(
        self,
        scenes: list[SceneInput],
        output_path: Path,
    ) -> None:
        """Stitch per-scene image+audio clips into a single MP4 video."""
        ...
