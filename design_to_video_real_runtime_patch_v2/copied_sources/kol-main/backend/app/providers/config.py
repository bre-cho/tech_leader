import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def provider_default_dry_run() -> bool:
    return env_bool("PROVIDER_DEFAULT_DRY_RUN", False)
