import base64, hashlib, os, time
from typing import Dict, Any

class HiDreamProvider:
    """Production-ready adapter boundary.

    Modes:
    - mock: deterministic artifact metadata for local/dev tests.
    - hf_inference: HTTP integration point for HuggingFace endpoint.
    - local_diffusers: integration boundary for GPU server implementation.

    This MVP intentionally separates orchestration contracts from GPU runtime so devs can
    connect the actual HiDream runner without rewriting business logic.
    """

    def generate(self, compiled: Dict[str, Any]) -> Dict[str, Any]:
        provider = compiled.get("provider", "mock")
        if provider == "mock":
            return self._mock(compiled)
        if provider == "hf_inference":
            return self._hf_placeholder(compiled)
        if provider == "local_diffusers":
            return self._local_placeholder(compiled)
        raise ValueError(f"Unsupported provider: {provider}")

    def _mock(self, compiled: Dict[str, Any]) -> Dict[str, Any]:
        payload = (compiled["prompt"] + compiled["negative_prompt"]).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        return {
            "provider": "mock",
            "status": "succeeded",
            "artifact_id": f"artifact_{digest[:12]}",
            "checksum": digest,
            "url": f"/artifacts/{digest[:12]}.json",
            "metadata": {
                "note": "Mock provider generated deterministic artifact contract. Replace provider=local_diffusers for GPU runtime.",
                "aspect_ratio": compiled["aspect_ratio"],
                "quality": compiled["quality"]
            }
        }

    def _hf_placeholder(self, compiled: Dict[str, Any]) -> Dict[str, Any]:
        token = os.getenv("HF_TOKEN")
        endpoint = os.getenv("HIDREAM_HF_ENDPOINT")
        if not token or not endpoint:
            return {"provider": "hf_inference", "status": "blocked", "error": "Missing HF_TOKEN or HIDREAM_HF_ENDPOINT"}
        return {"provider": "hf_inference", "status": "ready_to_call", "endpoint": endpoint, "payload": compiled}

    def _local_placeholder(self, compiled: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = os.getenv("HIDREAM_LOCAL_ENDPOINT", "http://localhost:8188/generate")
        return {"provider": "local_diffusers", "status": "ready_to_call", "endpoint": endpoint, "payload": compiled}
