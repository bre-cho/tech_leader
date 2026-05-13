import hashlib, json, uuid
from pathlib import Path
from app.creative_os_mvp.core.config import settings
from app.creative_os_mvp.models.schemas import Artifact

class ArtifactStore:
    def save(self, data: bytes, artifact_type: str, mime_type: str, metadata: dict) -> Artifact:
        aid=str(uuid.uuid4())
        ext = ".png" if mime_type == "image/png" else ".bin"
        path=settings.artifacts_dir / f"{aid}{ext}"
        path.write_bytes(data)
        checksum=hashlib.sha256(data).hexdigest()
        manifest={"artifact_id":aid, "artifact_type":artifact_type, "mime_type":mime_type, "size_bytes":len(data), "checksum_sha256":checksum, "metadata":metadata}
        (settings.artifacts_dir / f"{aid}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return Artifact(artifact_id=aid, artifact_type=artifact_type, path=str(path), url=f"/api/v1/artifacts/{aid}", mime_type=mime_type, size_bytes=len(data), checksum_sha256=checksum, metadata=metadata)

    def get_path(self, artifact_id: str) -> Path:
        for ext in [".png", ".jpg", ".bin"]:
            p=settings.artifacts_dir / f"{artifact_id}{ext}"
            if p.exists(): return p
        raise FileNotFoundError(artifact_id)
