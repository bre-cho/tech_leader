from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "Agentic Creative Operating Environment"
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_creative.db")
    strict_mode: bool = os.getenv("AGENTIC_STRICT_MODE", "true").lower() == "true"
    winner_dna_threshold: int = int(os.getenv("WINNER_DNA_THRESHOLD", "85"))
    hidream_provider: str = os.getenv("HIDREAM_PROVIDER", "hf_inference")
    hidream_model_id: str = os.getenv("HIDREAM_MODEL_ID", "HiDream-ai/HiDream-O1-Image")
    hidream_hf_token: str = os.getenv("HUGGINGFACE_TOKEN", "")
    artifact_dir: str = os.getenv("ARTIFACT_DIR", "./artifacts")
    hidream_timeout_seconds: int = int(os.getenv("HIDREAM_TIMEOUT_SECONDS", "180"))
    cors_allow_origins: str = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    )
    write_api_keys: str = os.getenv("WRITE_API_KEYS", "")
    require_write_auth: bool = os.getenv("REQUIRE_WRITE_AUTH", "false").lower() == "true"

settings = Settings()
