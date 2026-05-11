
from __future__ import annotations

from pathlib import Path
from typing import Iterable

IGNORE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".turbo", ".cache", ".code-intelligence",
}

SUPPORTED_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yml", ".yaml", ".sql", ".sh", ".toml"
}


def iter_source_files(repo_root: str) -> Iterable[Path]:
    root = Path(repo_root)
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SUPPORTED_EXTS:
            yield path


def detect_layer(path: Path) -> str:
    p = path.as_posix()
    if p.startswith("frontend/"):
        return "vite-render-studio"
    if p.startswith("backend/app/api/"):
        return "fastapi-api-router"
    if p.startswith("backend/app/workers/"):
        return "celery-worker"
    if p.startswith("backend/app/services/"):
        return "fastapi-service-layer"
    if p.startswith("backend/app/storyboard_engine/") or p.startswith("backend/app/storyboard_production/"):
        return "storyboard-layer"
    if p.startswith("backend/app/providers/") or "provider" in p:
        return "provider-layer"
    if p.startswith("backend/alembic/"):
        return "database-migration"
    if p.startswith("backend/tests/") or p.startswith("tests/"):
        return "test-suite"
    if p.startswith("scripts/"):
        return "ops-script"
    if p.startswith("docs/"):
        return "documentation"
    return "repo-root"


def detect_domain(path: Path, text: str = "") -> str:
    hay = (path.as_posix() + "\n" + text[:5000]).lower()
    rules = [
        ("multi_angle", "multi-angle-storyboard"),
        ("storyboard", "storyboard-engine"),
        ("poster_video", "poster-to-storyboard"),
        ("higgsfield", "higgsfield-seedance2"),
        ("seedance", "multi-provider"),
        ("kling", "multi-provider"),
        ("runway", "multi-provider"),
        ("veo", "multi-provider"),
        ("volcengine", "multi-provider"),
        ("provider", "multi-provider"),
        ("smart_subtitle", "smart-subtitle"),
        ("subtitle", "smart-subtitle"),
        ("karaoke", "smart-subtitle"),
        ("audio", "audio-engine"),
        ("voice", "audio-engine"),
        ("elevenlabs", "audio-engine"),
        ("avatar", "avatar-engine"),
        ("drama", "drama-engine"),
        ("render_production", "production-render"),
        ("production_render", "production-render"),
        ("ffmpeg", "production-render"),
        ("artifact", "artifact-contracts"),
        ("storage", "artifact-contracts"),
        ("factory", "ai-video-factory"),
        ("viral", "viral-optimizer"),
        ("analytics", "analytics-feedback"),
        ("playwright", "html-render"),
        ("html_scene", "html-render"),
        ("code_intelligence", "code-intelligence"),
        ("production_coordinator", "production-coordinator"),
    ]
    for key, domain in rules:
        if key in hay:
            return domain
    return "general"
