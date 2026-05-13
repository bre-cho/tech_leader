from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.creative_os_mvp.storage.artifacts import ArtifactStore

router=APIRouter()
store=ArtifactStore()

@router.get("/{artifact_id}")
def get_artifact(artifact_id: str):
    try:
        p=store.get_path(artifact_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(p)
