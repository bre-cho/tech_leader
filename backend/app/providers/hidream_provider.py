from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Dict, Any


class HiDreamProvider:
    '''
    Provider boundary.
    - mock: deterministic local artifact for dev/CI.
    - hf_inference/local_diffusers: reserved runtime slots for GPU integration.
    '''

    def __init__(self, mode: str = "mock", storage_dir: str = "storage/artifacts"):
        self.mode = mode
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, prompt: str, negative_prompt: str, metadata: Dict[str, Any]):
        if self.mode != "mock":
            # This boundary is intentionally explicit: production teams can plug HF endpoint,
            # Replicate, ComfyUI, RunningHub, or local diffusers here without touching orchestrator.
            return {
                "status": "queued",
                "provider": self.mode,
                "url": metadata.get("external_url", ""),
                "message": "Provider boundary reached. Configure HIDREAM_ENDPOINT for real GPU inference.",
            }

        payload = (prompt + negative_prompt + str(metadata)).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        path = self.storage_dir / f"hidream_mock_{digest[:16]}.txt"
        path.write_text(prompt + "\n\nNEGATIVE:\n" + negative_prompt, encoding="utf-8")
        return {
            "status": "completed",
            "provider": "mock",
            "path": str(path),
            "checksum": digest,
            "mime_type": "text/plain",
        }
