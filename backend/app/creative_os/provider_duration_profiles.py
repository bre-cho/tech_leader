from pydantic import BaseModel

class ProviderDurationProfile(BaseModel):
    provider: str
    recommended_duration_per_scene: float
    max_duration_per_scene: float
    default_planned_batch_size: int
    max_concurrent_render: int = 1
    cooldown_seconds: int
    retry_limit: int

PROVIDER_DURATION_PROFILES = {
    "veo": ProviderDurationProfile(provider="veo", recommended_duration_per_scene=8, max_duration_per_scene=10, default_planned_batch_size=4, cooldown_seconds=8, retry_limit=2),
    "runway": ProviderDurationProfile(provider="runway", recommended_duration_per_scene=5, max_duration_per_scene=10, default_planned_batch_size=6, cooldown_seconds=5, retry_limit=2),
    "kling": ProviderDurationProfile(provider="kling", recommended_duration_per_scene=5, max_duration_per_scene=10, default_planned_batch_size=6, cooldown_seconds=6, retry_limit=2),
    "seedance": ProviderDurationProfile(provider="seedance", recommended_duration_per_scene=6, max_duration_per_scene=10, default_planned_batch_size=6, cooldown_seconds=5, retry_limit=2),
    "seedance2": ProviderDurationProfile(provider="seedance2", recommended_duration_per_scene=5, max_duration_per_scene=5, default_planned_batch_size=1, cooldown_seconds=5, retry_limit=3),
    "seedance2-fast": ProviderDurationProfile(provider="seedance2-fast", recommended_duration_per_scene=5, max_duration_per_scene=5, default_planned_batch_size=1, cooldown_seconds=5, retry_limit=3),
}

def get_provider_profile(provider: str) -> ProviderDurationProfile:
    key = provider.lower().strip()
    if key not in PROVIDER_DURATION_PROFILES:
        raise ValueError(f"Unsupported provider: {provider}")
    return PROVIDER_DURATION_PROFILES[key]
