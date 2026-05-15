import hashlib
from pathlib import Path
from app.lipdub.contracts import LipDubArtifact
def checksum_text(v): return hashlib.sha256(v.encode()).hexdigest()
def write_mock_artifact(path, content, provider, metadata):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')
    d=checksum_text(content)
    return LipDubArtifact(artifact_id='lipdub_'+d[:16], artifact_type='lipdub_video_plan', path_or_url=str(p), provider=provider, checksum=d, metadata=metadata)
