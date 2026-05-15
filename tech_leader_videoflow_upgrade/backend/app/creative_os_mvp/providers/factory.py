from app.creative_os_mvp.core.config import settings
from app.creative_os_mvp.providers.mock import MockCommercialProvider
from app.creative_os_mvp.providers.hf_inference import HFInferenceProvider
from app.creative_os_mvp.providers.local_diffusers import LocalDiffusersProvider

def get_provider():
    if settings.provider == "hf_inference":
        return HFInferenceProvider()
    if settings.provider == "local_diffusers":
        return LocalDiffusersProvider()
    return MockCommercialProvider()
