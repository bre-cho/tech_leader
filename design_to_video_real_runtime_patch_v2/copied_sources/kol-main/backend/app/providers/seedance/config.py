from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


_ENV_CACHE: dict[str, str] | None = None


def _load_repo_env() -> dict[str, str]:
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE

    env_map: dict[str, str] = {}
    env_file = Path(__file__).resolve().parents[4] / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env_map[key.strip()] = value.strip()
    _ENV_CACHE = env_map
    return env_map


def _env_value(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is not None and value != "":
        return value
    return _load_repo_env().get(name, default)


@dataclass(frozen=True)
class SeedanceRouteConfig:
    route: str
    api_key: str
    base_url: str
    create_path: str
    retrieve_path: str
    cancel_path: str | None
    model: str
    preferred_video_models: tuple[str, ...] = ()
    timeout_seconds: int = 60
    poll_interval_seconds: int = 8
    max_poll_seconds: int = 1800

    @classmethod
    def from_env(cls) -> "SeedanceRouteConfig":
        api_key = _env_value("SEEDANCE_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Missing SEEDANCE_API_KEY")

        return cls(
            route=_env_value("SEEDANCE_ROUTE", "byteplus").strip().lower(),
            api_key=api_key,
            base_url=_env_value("SEEDANCE_API_BASE_URL", "https://ark.ap-southeast.bytepluses.com").rstrip("/"),
            create_path=_env_value("SEEDANCE_CREATE_PATH", "/api/v3/contents/generations/tasks"),
            retrieve_path=_env_value("SEEDANCE_RETRIEVE_PATH", "/api/v3/contents/generations/tasks/{task_id}"),
            cancel_path=_env_value("SEEDANCE_CANCEL_PATH", "/api/v3/contents/generations/tasks/{task_id}"),
            model=_env_value("SEEDANCE_MODEL", "seedance-2-0"),
            preferred_video_models=tuple(
                value.strip()
                for value in _env_value(
                    "SEEDANCE_VIDEO_MODEL_CANDIDATES",
                    "",
                ).split(",")
                if value.strip()
            ),
            timeout_seconds=int(_env_value("SEEDANCE_TIMEOUT_SECONDS", "60")),
            poll_interval_seconds=int(_env_value("SEEDANCE_POLL_INTERVAL_SECONDS", "8")),
            max_poll_seconds=int(_env_value("SEEDANCE_MAX_POLL_SECONDS", "1800")),
        )
