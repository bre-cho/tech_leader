from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class VolcengineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    VOLCENGINE_ENABLED: bool = False
    VOLCENGINE_MODE: Literal["ark_api_key", "disabled"] = "ark_api_key"

    VOLCENGINE_ARK_API_KEY: str | None = None
    VOLCENGINE_ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    VOLCENGINE_ARK_REGION: str = "cn-beijing"
    VOLCENGINE_ARK_FALLBACK_BASE_URL: str | None = None

    VOLCENGINE_DEFAULT_TEXT_MODEL: str = "doubao-seed-1-6-250615"
    VOLCENGINE_DEFAULT_VIDEO_MODEL: str | None = None

    VOLCENGINE_TIMEOUT_SECONDS: int = 90
    VOLCENGINE_MAX_RETRIES: int = 3
    VOLCENGINE_HEALTH_MODEL: str | None = None

    VOLCENGINE_ACCESS_KEY_ID: str | None = None
    VOLCENGINE_SECRET_ACCESS_KEY: str | None = None


settings = VolcengineSettings()
