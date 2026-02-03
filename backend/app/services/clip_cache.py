import hashlib
import json
from pathlib import Path


class ClipCache:
    """JSON manifest cache for generated video clips."""

    def __init__(self, cache_path: Path) -> None:
        self._path = cache_path
        self._data: dict[str, dict] = {}
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    @staticmethod
    def compute_hash(visual_desc: str, scene_title: str, duration: int) -> str:
        key = f"{visual_desc}|{scene_title}|{duration}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def is_valid(self, index: int, hash_val: str, path: Path) -> bool:
        entry = self._data.get(str(index))
        if not entry:
            return False
        return entry.get("hash") == hash_val and Path(entry.get("path", "")).exists()

    def set(self, index: int, hash_val: str, path: Path) -> None:
        self._data[str(index)] = {"hash": hash_val, "path": str(path)}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))
