from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    USE_MOCK_AI: bool = True
    USE_MOCK_TTS: bool = True
    TTS_VOICE: str = "alloy"
    DATABASE_URL: str = "sqlite+aiosqlite:///./studyscenes.db"
    STORAGE_PATH: str = "./storage"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    OPENAI_API_KEY: str = ""
    VIDEO_PROVIDER: str = "mock"
    RUNWAY_API_KEY: str = ""
    SCENE_CLIP_SECONDS: int = 6
    MAX_TOTAL_VIDEO_SECONDS: int = 90

    @property
    def storage_dir(self) -> Path:
        p = Path(self.STORAGE_PATH)
        p.mkdir(parents=True, exist_ok=True)
        return p

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
