from __future__ import annotations

import logging
import os
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    voice_consent_min_chars: int = _get_int("VOICE_CONSENT_MIN_CHARS", 20)
    require_voice_consent: bool = _get_bool("REQUIRE_VOICE_CONSENT", True)
    default_music_gain_db: int = _get_int("DEFAULT_MUSIC_GAIN_DB", -18)
    default_narration_gain_db: int = _get_int("DEFAULT_NARRATION_GAIN_DB", 0)
    default_music_ducking_db: int = _get_int("DEFAULT_MUSIC_DUCKING_DB", 10)
    default_breath_preset: str = os.getenv("DEFAULT_BREATH_PRESET", "natural")
    elevenlabs_enable_music: bool = _get_bool("ELEVENLABS_ENABLE_MUSIC", False)
    elevenlabs_default_similarity_boost: float = _get_float("ELEVENLABS_DEFAULT_SIMILARITY_BOOST", 0.8)
    elevenlabs_default_stability: float = _get_float("ELEVENLABS_DEFAULT_STABILITY", 0.45)
    elevenlabs_tts_output_format: str = os.getenv("ELEVENLABS_TTS_OUTPUT_FORMAT", "mp3_44100_128")
    elevenlabs_base_url: str = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io")
    ffprobe_binary: str = os.getenv("FFPROBE_BINARY", "ffprobe")
    observability_enabled: bool = _get_bool("OBSERVABILITY_ENABLED", True)
    notification_plane_enabled: bool = _get_bool("NOTIFICATION_PLANE_ENABLED", True)
    decision_engine_enabled: bool = _get_bool("DECISION_ENGINE_ENABLED", True)
    decision_engine_policy_path: str | None = os.getenv("DECISION_ENGINE_POLICY_PATH")
    control_plane_enabled: bool = _get_bool("CONTROL_PLANE_ENABLED", True)
    default_dispatch_batch_limit: int = _get_int("DEFAULT_DISPATCH_BATCH_LIMIT", 10)
    default_poll_countdown_seconds: int = _get_int("DEFAULT_POLL_COUNTDOWN_SECONDS", 60)
    autopilot_control_fabric_enabled: bool = _get_bool("AUTOPILOT_CONTROL_FABRIC_ENABLED", True)

    audio_upload_dir: str = os.getenv("AUDIO_UPLOAD_DIR", "/app/storage/audio_uploads")
    audio_output_dir: str = os.getenv("AUDIO_OUTPUT_DIR", "/app/storage/artifacts/audio")
    video_output_dir: str = os.getenv("VIDEO_OUTPUT_DIR", "/app/storage/artifacts/video")
    audio_output_format: str = os.getenv("AUDIO_OUTPUT_FORMAT", "mp3_44100_128")
    audio_upload_to_object_storage: bool = _get_bool("AUDIO_UPLOAD_TO_OBJECT_STORAGE", True)
    ffmpeg_binary: str = os.getenv("FFMPEG_BINARY", "ffmpeg")
    elevenlabs_api_key: str | None = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_tts_model_id: str = os.getenv("ELEVENLABS_TTS_MODEL_ID", "eleven_multilingual_v2")
    default_music_duration_seconds: int = _get_int("DEFAULT_MUSIC_DURATION_SECONDS", 30)
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/render_factory")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    storage_root: str = os.getenv("STORAGE_ROOT", "/app/storage")
    storage_public_base_url: str = os.getenv("STORAGE_PUBLIC_BASE_URL", "/storage")
    render_cache_dir: str = os.getenv("RENDER_CACHE_DIR", "/app/storage/render_cache")
    render_output_dir: str = os.getenv("RENDER_OUTPUT_DIR", "/app/storage/render_outputs")
    object_storage_provider: str = os.getenv("OBJECT_STORAGE_PROVIDER", "minio")
    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL")
    s3_access_key_id: str | None = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = os.getenv("S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "render-assets")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_public_base_url: str | None = os.getenv("S3_PUBLIC_BASE_URL")
    signed_url_expires_seconds: int = _get_int("SIGNED_URL_EXPIRES_SECONDS", 3600)
    google_cloud_project: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    google_genai_use_vertex: bool = _get_bool("GOOGLE_GENAI_USE_VERTEX", True)
    google_application_credentials: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    veo_default_model: str = os.getenv("VEO_DEFAULT_MODEL", "veo-3.1-generate-001")
    veo_fast_model: str = os.getenv("VEO_FAST_MODEL", "veo-3.1-fast-generate-001")
    veo_api_base_url: str | None = os.getenv("VEO_API_BASE_URL")
    veo_api_key: str | None = os.getenv("VEO_API_KEY")
    veo_submit_path: str = os.getenv("VEO_SUBMIT_PATH", "/v1/videos:generate")
    veo_status_path_template: str = os.getenv("VEO_STATUS_PATH_TEMPLATE", "/v1/operations/{operation_name}")
    veo_output_gcs_uri: str | None = os.getenv("VEO_OUTPUT_GCS_URI")
    veo_batch_max_scripts: int = _get_int("VEO_BATCH_MAX_SCRIPTS", 100)
    veo_enable_sound_generation: bool = _get_bool("VEO_ENABLE_SOUND_GENERATION", False)
    veo_enable_reference_preview: bool = _get_bool("VEO_ENABLE_REFERENCE_PREVIEW", False)
    veo_reference_preview_model: str = os.getenv("VEO_REFERENCE_PREVIEW_MODEL", "veo-3.1-generate-preview")

    runway_base_url: str = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com")
    runway_default_model: str = os.getenv("RUNWAY_DEFAULT_MODEL", "gen4.5")
    runwayml_api_secret: str | None = os.getenv("RUNWAYML_API_SECRET")
    runway_api_key: str | None = os.getenv("RUNWAY_API_KEY")
    runway_api_version: str | None = os.getenv("RUNWAY_API_VERSION")

    provider_callback_use_relay: bool = _get_bool("PROVIDER_CALLBACK_USE_RELAY", False)
    provider_callback_public_base_url: str | None = os.getenv("PROVIDER_CALLBACK_PUBLIC_BASE_URL")
    provider_callback_relay_path_template: str = os.getenv("PROVIDER_CALLBACK_RELAY_PATH_TEMPLATE", "/hooks/{provider}")
    provider_max_retries: int = _get_int("PROVIDER_MAX_RETRIES", 2)
    provider_retry_base_seconds: int = _get_int("PROVIDER_RETRY_BASE_SECONDS", 2)
    provider_allow_mock_fallback: bool = _get_bool("PROVIDER_ALLOW_MOCK_FALLBACK", False)
    provider_submit_rate_limit_per_minute: int = _get_int("PROVIDER_SUBMIT_RATE_LIMIT_PER_MINUTE", 120)
    provider_daily_submit_quota: int = _get_int("PROVIDER_DAILY_SUBMIT_QUOTA", 5000)
    provider_daily_cost_limit_usd: float = _get_float("PROVIDER_DAILY_COST_LIMIT_USD", 0.0)
    provider_idempotency_header: str = os.getenv("PROVIDER_IDEMPOTENCY_HEADER", "Idempotency-Key")
    veo_estimated_cost_per_submit_usd: float = _get_float("VEO_ESTIMATED_COST_PER_SUBMIT_USD", 0.0)
    provider_callback_shared_secret: str | None = os.getenv("PROVIDER_CALLBACK_SHARED_SECRET")
    provider_relay_shared_secret: str | None = os.getenv("PROVIDER_RELAY_SHARED_SECRET")
    veo_relay_shared_secret: str | None = os.getenv("VEO_RELAY_SHARED_SECRET")
    provider_ingress_signature_ttl_seconds: int = _get_int("PROVIDER_INGRESS_SIGNATURE_TTL_SECONDS", 300)
    provider_http_timeout_seconds: int = _get_int("PROVIDER_HTTP_TIMEOUT_SECONDS", 120)
    provider_dispatch_timeout_seconds: int = _get_int("PROVIDER_DISPATCH_TIMEOUT_SECONDS", 120)
    provider_poll_timeout_seconds: int = _get_int("PROVIDER_POLL_TIMEOUT_SECONDS", 60)
    celery_task_time_limit: int = _get_int("CELERY_TASK_TIME_LIMIT", 1800)
    celery_task_soft_time_limit: int = _get_int("CELERY_TASK_SOFT_TIME_LIMIT", 1500)
    celery_worker_prefetch_multiplier: int = _get_int("CELERY_WORKER_PREFETCH_MULTIPLIER", 1)
    celery_task_acks_late: bool = _get_bool("CELERY_TASK_ACKS_LATE", True)

    # RAG / Embedding settings
    rag_enabled: bool = _get_bool("RAG_ENABLED", True)
    rag_chunk_size: int = _get_int("RAG_CHUNK_SIZE", 400)
    rag_chunk_overlap: int = _get_int("RAG_CHUNK_OVERLAP", 80)
    rag_top_k: int = _get_int("RAG_TOP_K", 5)
    rag_embedding_backend: str = os.getenv("RAG_EMBEDDING_BACKEND", "tfidf")  # "tfidf" | "openrouter"
    rag_embedding_model: str = os.getenv("RAG_EMBEDDING_MODEL", "openai/text-embedding-ada-002")
    rag_vector_store_path: str = os.getenv("RAG_VECTOR_STORE_PATH", "/app/storage/rag_index.json")
    rag_docs_root: str = os.getenv("RAG_DOCS_ROOT", "docs")
    rag_llm_system_prompt: str = os.getenv(
        "RAG_LLM_SYSTEM_PROMPT",
        "You are an operations assistant for the Render Factory platform. "
        "Answer questions ONLY using the provided context passages. "
        "If the answer is not found in the context, say 'I don't have enough context to answer that.' "
        "Do not speculate or fabricate information.",
    )

    allow_stub_embedding: bool = _get_bool("ALLOW_STUB_EMBEDDING", False)

    # ML / prediction settings
    ml_enabled: bool = _get_bool("ML_ENABLED", True)
    ml_model_path: str = os.getenv("ML_MODEL_PATH", "/app/storage/ml_render_predictor.json")
    ml_min_training_samples: int = _get_int("ML_MIN_TRAINING_SAMPLES", 10)
    ml_feature_lookback_days: int = _get_int("ML_FEATURE_LOOKBACK_DAYS", 30)

    # LLM function calling
    llm_function_calling_enabled: bool = _get_bool("LLM_FUNCTION_CALLING_ENABLED", True)
    llm_max_tool_calls_per_request: int = _get_int("LLM_MAX_TOOL_CALLS_PER_REQUEST", 5)

    # Authentication
    # AUTH_ENABLED=true (default in production) requires a valid Bearer token on
    # protected endpoints.  Set to false only in local dev / CI environments.
    auth_enabled: bool = _get_bool("AUTH_ENABLED", False)
    # JWT secret used to sign/verify internal tokens (HS256).
    # Must be set in production when AUTH_ENABLED=true.
    jwt_secret_key: str | None = os.getenv("JWT_SECRET_KEY")
    # Static API key accepted as an alternative to JWT tokens.
    # Useful for machine-to-machine calls where issuing a JWT is inconvenient.
    api_key: str | None = os.getenv("API_KEY")

    # Legacy environment alias — some older deployments set ACSE_ENV instead of
    # APP_ENV.  Reading it here prevents AttributeError in provider_mock_enabled()
    # which checks both fields.  APP_ENV takes precedence.
    acse_env: str | None = os.getenv("ACSE_ENV")

    # Drama TTS — set DRAMA_TTS_ENABLED=true in production to enable real TTS.
    # When false the stub (example.invalid URL) is used and will be blocked by
    # fake_success_guard in production, causing render failures.
    drama_tts_enabled: bool = _get_bool("DRAMA_TTS_ENABLED", False)

    # Learning loop backend — "db" for production (requires DATABASE_URL and
    # the video_provider_outcomes table), "file" for single-process development,
    # "noop" for explicit non-persistent mode.
    learning_loop_backend: str = os.getenv("LEARNING_LOOP_BACKEND", "noop")
    jwt_secret_keys: str | None = os.getenv("JWT_SECRET_KEYS")
    jwt_expected_issuer: str | None = os.getenv("JWT_EXPECTED_ISSUER")
    jwt_expected_audience: str | None = os.getenv("JWT_EXPECTED_AUDIENCE")


settings = Settings()
_app_env = settings.app_env.strip().lower()
if _app_env == "production" and settings.provider_allow_mock_fallback:
    raise ValueError("PROVIDER_ALLOW_MOCK_FALLBACK must be false when APP_ENV=production")
# P0-3: Also block mock fallback in staging — staging receives real traffic
# and a mock fallback silently produces fake render results that look successful.
if _app_env == "staging" and settings.provider_allow_mock_fallback:
    raise ValueError(
        "PROVIDER_ALLOW_MOCK_FALLBACK must be false when APP_ENV=staging. "
        "Staging environments receive real traffic; a mock fallback would silently "
        "produce fake render results that bypass the real provider pipeline."
    )
if _app_env not in {"", "dev", "development", "test", "testing", "local"} and settings.learning_loop_backend.strip().lower() == "file":
    logger.warning(
        "LEARNING_LOOP_BACKEND=file is active in APP_ENV=%r. "
        "Use LEARNING_LOOP_BACKEND=db for shared persistent learning or noop only for intentional stateless mode.",
        settings.app_env,
    )
if _app_env == "production":
    if not settings.public_base_url:
        raise ValueError(
            "PUBLIC_BASE_URL is required when APP_ENV=production. "
            "Set PUBLIC_BASE_URL to the real public hostname before deploying."
        )
    if "localhost" in settings.public_base_url:
        raise ValueError(
            "PUBLIC_BASE_URL contains 'localhost' while APP_ENV=production. "
            "Set PUBLIC_BASE_URL to the real public hostname before deploying."
        )
    # P1-B: Auth must be enabled in production to prevent unauthenticated access.
    # Emergency override: set ALLOW_AUTH_DISABLED_IN_PROD=true to bypass this check
    # (requires explicit acknowledgement; always emits a CRITICAL audit warning).
    if not settings.auth_enabled:
        _allow_auth_disabled = os.getenv("ALLOW_AUTH_DISABLED_IN_PROD", "").strip().lower() in {"1", "true", "yes"}
        if _allow_auth_disabled:
            logger.critical(
                "SECURITY AUDIT WARNING: AUTH_ENABLED=false in production is explicitly permitted "
                "via ALLOW_AUTH_DISABLED_IN_PROD=true. All protected endpoints are publicly accessible. "
                "Remove ALLOW_AUTH_DISABLED_IN_PROD and set AUTH_ENABLED=true before serving real traffic."
            )
        else:
            raise ValueError(
                "AUTH_ENABLED must be true when APP_ENV=production. "
                "Set AUTH_ENABLED=true and configure JWT_SECRET_KEY or API_KEY before deploying. "
                "Emergency override: set ALLOW_AUTH_DISABLED_IN_PROD=true (audit warning will be emitted)."
            )
    # P1-C: Callback shared secret must be set in production to prevent spoofed
    # provider callbacks (SSRF/replay attack surface).
    if not settings.provider_callback_shared_secret:
        raise ValueError(
            "PROVIDER_CALLBACK_SHARED_SECRET must be set when APP_ENV=production. "
            "Set it to a strong random secret to authenticate incoming provider callbacks."
        )
    # P0.3: Drama TTS must be enabled in production — the stub URL will be blocked
    # by fake_success_guard causing render failures if TTS is requested.
    if not settings.drama_tts_enabled:
        raise ValueError(
            "DRAMA_TTS_ENABLED must be true when APP_ENV=production. "
            "Set DRAMA_TTS_ENABLED=true and configure ELEVENLABS_API_KEY (or GOOGLE_TTS_KEY) "
            "before deploying.  The TTS stub URL (example.invalid) is blocked in production "
            "by fake_success_guard and will cause drama render failures."
        )
    # C2/C6: When TTS is enabled, the API key must be present — otherwise every
    # TTS call will fail at runtime with an unhelpful authentication error.
    if not settings.elevenlabs_api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY must be set when APP_ENV=production and DRAMA_TTS_ENABLED=true. "
            "Configure the API key before deploying to avoid TTS authentication failures."
        )
    # P1.1: Learning loop backend must be 'db' in production to avoid silently
    # dropping provider outcome signals and degrading routing quality.
    if settings.learning_loop_backend.strip().lower() != "db":
        raise ValueError(
            "LEARNING_LOOP_BACKEND must be 'db' when APP_ENV=production. "
            "Set LEARNING_LOOP_BACKEND=db and ensure the video_provider_outcomes table "
            "exists (alembic upgrade head).  Other values silently drop provider learning "
            "signals and degrade routing quality over time."
        )
    # Cross-field: ElevenLabs API key must be set when TTS or music is enabled.
    if settings.drama_tts_enabled and not settings.elevenlabs_api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY must be set when DRAMA_TTS_ENABLED=true and APP_ENV=production. "
            "Set ELEVENLABS_API_KEY to authenticate drama TTS synthesis requests."
        )
    if settings.elevenlabs_enable_music and not settings.elevenlabs_api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY must be set when ELEVENLABS_ENABLE_MUSIC=true and APP_ENV=production. "
            "Set ELEVENLABS_API_KEY to authenticate ElevenLabs music generation requests."
        )
    # Cross-field: JWT secret must be present when auth is enabled and no static
    # API key is configured (otherwise the only auth mechanism is unset).
    if settings.auth_enabled and not settings.jwt_secret_key and not settings.api_key:
        raise ValueError(
            "JWT_SECRET_KEY or API_KEY must be set when AUTH_ENABLED=true and APP_ENV=production. "
            "At least one of these must be configured to authenticate API requests."
        )

# P1.6: Auth must also be enabled in staging — staging receives real or near-real
# traffic and must not expose unauthenticated endpoints.
if _app_env == "staging":
    if not settings.auth_enabled:
        raise ValueError(
            "AUTH_ENABLED must be true when APP_ENV=staging. "
            "Staging environments receive real traffic and must not expose unauthenticated "
            "API endpoints.  Set AUTH_ENABLED=true and configure JWT_SECRET_KEY or API_KEY."
        )
    # P1.1-staging: Learning loop backend must be 'db' in staging — same requirement
    # as production to ensure provider learning signals are shared across workers and
    # staging routing quality mirrors production.
    if settings.learning_loop_backend.strip().lower() != "db":
        raise ValueError(
            "LEARNING_LOOP_BACKEND must be 'db' when APP_ENV=staging. "
            "Set LEARNING_LOOP_BACKEND=db and ensure the video_provider_outcomes table "
            "exists (alembic upgrade head).  Other values silently drop provider learning "
            "signals and degrade routing quality."
        )
