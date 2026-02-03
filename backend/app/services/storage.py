from pathlib import Path
import shutil

from app.core.config import settings


class LocalFileStorage:
    def __init__(self):
        self.base = settings.storage_dir

    def project_dir(self, project_id: str) -> Path:
        d = self.base / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def images_dir(self, project_id: str) -> Path:
        d = self.project_dir(project_id) / "images"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def audio_dir(self, project_id: str) -> Path:
        d = self.project_dir(project_id) / "audio"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def clips_dir(self, project_id: str) -> Path:
        d = self.project_dir(project_id) / "clips"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def scene_clip_path(self, project_id: str, index: int) -> Path:
        return self.clips_dir(project_id) / f"scene_{index:03d}.mp4"

    def clip_cache_path(self, project_id: str) -> Path:
        return self.clips_dir(project_id) / "cache.json"

    def video_dir(self, project_id: str) -> Path:
        d = self.project_dir(project_id) / "video"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def scene_image_path(self, project_id: str, index: int) -> Path:
        return self.images_dir(project_id) / f"scene_{index:03d}.png"

    def narration_path(self, project_id: str) -> Path:
        return self.audio_dir(project_id) / "narration.mp3"

    def scene_audio_path(self, project_id: str, index: int) -> Path:
        return self.audio_dir(project_id) / f"scene_{index:03d}.wav"

    def video_output_path(self, project_id: str) -> Path:
        return self.video_dir(project_id) / "output.mp4"

    def delete_project_files(self, project_id: str) -> None:
        d = self.base / project_id
        if d.exists():
            shutil.rmtree(d)

    def relative_path(self, absolute: Path) -> str:
        """Return storage-relative path for URL construction."""
        return str(absolute.relative_to(self.base))
