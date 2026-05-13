from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "Agentic Creative Operating Environment"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_creative.db")
    strict_mode: bool = os.getenv("AGENTIC_STRICT_MODE", "true").lower() == "true"
    winner_dna_threshold: int = int(os.getenv("WINNER_DNA_THRESHOLD", "85"))

settings = Settings()
