
from __future__ import annotations
import hashlib, json, time, uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings
from app.schemas.hidream import HiDreamArtifact, HiDreamGenerateRequest, HiDreamPromptContract

class ArtifactStore:
    def __init__(self, base_dir: Optional[str] = None):
        self.base = Path(base_dir or settings.artifact_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def save_png(self, image_bytes: bytes, provider: str, req: HiDreamGenerateRequest, contract: HiDreamPromptContract) -> HiDreamArtifact:
        artifact_id = f"hidream_{int(time.time())}_{uuid.uuid4().hex[:10]}"
        folder = self.base / "hidream" / artifact_id
        folder.mkdir(parents=True, exist_ok=True)
        img_path = folder / "image.png"
        contract_path = folder / "replay_contract.json"
        img_path.write_bytes(image_bytes)
        checksum = hashlib.sha256(image_bytes).hexdigest()
        replay = {
            "request": req.model_dump(),
            "prompt_contract": contract.model_dump(),
            "provider": provider,
            "model_id": settings.hidream_model_id,
            "checksum_sha256": checksum,
        }
        contract_path.write_text(json.dumps(replay, ensure_ascii=False, indent=2), encoding="utf-8")
        return HiDreamArtifact(
            artifact_id=artifact_id,
            artifact_type="hidream_commercial_image",
            path=str(img_path),
            url=f"/artifacts/hidream/{artifact_id}/image.png",
            mime_type="image/png",
            size_bytes=img_path.stat().st_size,
            checksum_sha256=checksum,
            provider=provider,
            model_id=settings.hidream_model_id,
            seed=req.seed,
            replay_contract={"path": str(contract_path), "checksum_sha256": checksum},
        )
