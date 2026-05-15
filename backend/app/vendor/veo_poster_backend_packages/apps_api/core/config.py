from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_JWT_SECRET = "change-me"
_WEAK_DEV_SECRET = "dev-internal-secret"


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./poster_engine.db"
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    storage_dir: str = "/data/storage"
    adobe_mode: str = "mock"
    adobe_api_key: str | None = None
    adobe_client_id: str | None = None
    canva_mode: str = "mock"
    canva_client_id: str | None = None
    canva_client_secret: str | None = None
    canva_access_token: str | None = None
    canva_api_base_url: str = "https://api.canva.com"
    adobe_api_base_url: str = "https://firefly-api.adobe.io"
    adobe_poll_interval_seconds: float = 1.0
    adobe_poll_max_attempts: int = 20
    canva_poll_interval_seconds: float = 1.0
    canva_poll_max_attempts: int = 20
    # C3: Per-environment poll overrides for staging vs production.
    # When APP_ENV is "staging" these values take priority over the generic
    # poll settings above, allowing a slower staging API to complete without
    # hitting the production timeout ceiling.
    # Set ADOBE_POLL_MAX_ATTEMPTS_STAGING / CANVA_POLL_MAX_ATTEMPTS_STAGING
    # in the staging .env to override; production uses the generic values.
    adobe_poll_max_attempts_staging: int | None = None
    canva_poll_max_attempts_staging: int | None = None
    adobe_poll_interval_seconds_staging: float | None = None
    canva_poll_interval_seconds_staging: float | None = None
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    api_budget_per_project: int = 100
    idempotency_ttl_seconds: int = 3600
    request_log_level: str = "INFO"
    auth_jwt_secret: str = _WEAK_JWT_SECRET
    auth_jwt_algorithm: str = "HS256"
    dev_internal_token_secret: str = _WEAK_DEV_SECRET
    storage_provider: str = "local"
    storage_bucket: str = "poster-engine"
    storage_region: str = "us-east-1"
    storage_endpoint_url: str | None = None
    storage_access_key_id: str | None = None
    storage_secret_access_key: str | None = None
    storage_signed_url_expiry_seconds: int = 86400
    billing_default_quota_per_month: int = 1000
    # Rate limiting: max generate requests per user per minute (0 = disabled)
    rate_limit_generate_per_minute: int = 10
    # Projects stuck in 'generating' status for longer than this many minutes
    # are automatically reset to 'failed' by the cleanup_stuck_projects task.
    # Must be a positive integer; defaults to 30.
    stuck_project_timeout_minutes: int = 30
    # AI image upscale provider runtime. Use local for zero-key MVP; switch to
    # claid / picwish / pixelcut when provider credentials are configured.
    image_upscale_default_provider: str = "local"
    claid_api_key: str | None = None
    claid_api_base_url: str = "https://api.claid.ai"
    picwish_api_key: str | None = None
    picwish_api_base_url: str = "https://techhk.aoscdn.com"
    pixelcut_api_key: str | None = None
    pixelcut_api_base_url: str = "https://api.pixelcut.ai"

    @model_validator(mode="after")
    def check_stuck_timeout(self) -> "Settings":
        if self.stuck_project_timeout_minutes <= 0:
            raise ValueError("STUCK_PROJECT_TIMEOUT_MINUTES must be a positive integer")
        return self

    @property
    def effective_adobe_poll_max_attempts(self) -> int:
        """C3: Return staging override when APP_ENV is staging, else the generic value."""
        if self.app_env.lower() == "staging" and self.adobe_poll_max_attempts_staging is not None:
            return self.adobe_poll_max_attempts_staging
        return self.adobe_poll_max_attempts

    @property
    def effective_adobe_poll_interval_seconds(self) -> float:
        """C3: Return staging override when APP_ENV is staging, else the generic value."""
        if self.app_env.lower() == "staging" and self.adobe_poll_interval_seconds_staging is not None:
            return self.adobe_poll_interval_seconds_staging
        return self.adobe_poll_interval_seconds

    @property
    def effective_canva_poll_max_attempts(self) -> int:
        """C3: Return staging override when APP_ENV is staging, else the generic value."""
        if self.app_env.lower() == "staging" and self.canva_poll_max_attempts_staging is not None:
            return self.canva_poll_max_attempts_staging
        return self.canva_poll_max_attempts

    @property
    def effective_canva_poll_interval_seconds(self) -> float:
        """C3: Return staging override when APP_ENV is staging, else the generic value."""
        if self.app_env.lower() == "staging" and self.canva_poll_interval_seconds_staging is not None:
            return self.canva_poll_interval_seconds_staging
        return self.canva_poll_interval_seconds

    @model_validator(mode="after")
    def check_production_guards(self) -> "Settings":
        """Raise early if critical settings are unsafe for production."""
        if self.app_env.lower() not in {"prod", "production"}:
            return self
        errors: list[str] = []
        if self.adobe_mode.lower() == "mock":
            errors.append("ADOBE_MODE cannot be 'mock' in production")
        if self.canva_mode.lower() == "mock":
            errors.append("CANVA_MODE cannot be 'mock' in production")
        if self.auth_jwt_secret == _WEAK_JWT_SECRET:
            errors.append(
                f'AUTH_JWT_SECRET must be changed from the default "{_WEAK_JWT_SECRET}" in production'
            )
        if self.dev_internal_token_secret == _WEAK_DEV_SECRET:
            errors.append(
                f'DEV_INTERNAL_TOKEN_SECRET must be changed from the default "{_WEAK_DEV_SECRET}" in production'
            )
        if "sqlite" in self.database_url.lower():
            errors.append("DATABASE_URL must not use SQLite in production")
        if errors:
            raise ValueError("Production guard violations:\n" + "\n".join(f"  - {e}" for e in errors))
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
