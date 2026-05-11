
from pathlib import Path
from .schemas import ContextCore

DEFAULT_CONTEXT_CORE_PATH = Path(".trustgraph-runtime/video-factory-context-core.json")

def save_context_core(core: ContextCore, path: Path = DEFAULT_CONTEXT_CORE_PATH) -> ContextCore:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(core.model_dump_json(indent=2), encoding="utf-8")
    return core

def load_context_core(path: Path = DEFAULT_CONTEXT_CORE_PATH) -> ContextCore | None:
    if not path.exists():
        return None
    return ContextCore.model_validate_json(path.read_text(encoding="utf-8"))
