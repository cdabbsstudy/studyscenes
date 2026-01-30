from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    USE_MOCK_AI: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./studyscenes.db"
    STORAGE_PATH: str = "./storage"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    OPENAI_API_KEY: str = ""

    @property
    def storage_dir(self) -> Path:
        p = Path(self.STORAGE_PATH)
        p.mkdir(parents=True, exist_ok=True)
        return p

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
