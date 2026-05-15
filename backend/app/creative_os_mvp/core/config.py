from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    provider: str = "mock"
    storage_dir: Path = Path("./storage")
    memory_dir: Path = Path("./storage/memory")
    artifacts_dir: Path = Path("./storage/artifacts")
    hf_token: str | None = None
    hf_endpoint_url: str | None = None
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_prefix="CREATIVE_OS_")

settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
settings.memory_dir.mkdir(parents=True, exist_ok=True)
settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
