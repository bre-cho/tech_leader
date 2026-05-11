
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Tuple


def summarize_file(path: Path, text: str) -> str:
    hay = (path.as_posix() + "\n" + text[:4000]).lower()
    if "production_coordinator" in hay:
        return "Graph-driven coordinator that links independent modules into the closed-loop video production pipeline."
    if "storyboard" in hay:
        return "Storyboard planning, poster analysis, scene split, camera plan, cinematic prompt or render handoff."
    if "provider" in hay or any(x in hay for x in ["seedance", "kling", "runway", "veo"]):
        return "Multi-provider AI video generation routing, payload compilation, dispatch, polling or callback handling."
    if "render_production" in hay or "ffmpeg" in hay:
        return "Production render assembly: concat scene videos, mix audio, burn subtitles and export final.mp4."
    if "subtitle" in hay or "karaoke" in hay:
        return "Smart subtitle timing, ASS/SRT, karaoke highlighting, safe zone and subtitle burn-in."
    if "audio" in hay or "voice" in hay:
        return "Audio narration, clone voice, TTS, BGM, SFX or mix/mux subsystem."
    if "avatar" in hay:
        return "Avatar generation, acting, continuity, marketplace, governance or analytics subsystem."
    if "drama" in hay:
        return "Drama engine: tension, emotion, subtext, relationship, scene analysis or emotional arc."
    if "viral" in hay or "analytics" in hay or "factory" in hay:
        return "AI Video Factory feedback layer: analytics, viral scores, RL loop, A/B hook and thumbnail optimization."
    if path.as_posix().startswith("frontend/"):
        return "Vite frontend render studio UI component, page, state model or API client."
    return "Source file in kol-main AI Video Factory codebase."


def analyze_python(path: Path, text: str) -> Tuple[List[dict], List[dict]]:
    nodes, edges = [], []
    file_id = f"file:{path.as_posix()}"

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return nodes, edges

    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            node_id = f"class:{path.as_posix()}:{item.name}"
            nodes.append({"id": node_id, "type": "class", "name": item.name, "path": path.as_posix()})
            edges.append({"source": file_id, "target": node_id, "type": "owns", "label": "defines class"})
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node_id = f"function:{path.as_posix()}:{item.name}"
            nodes.append({"id": node_id, "type": "function", "name": item.name, "path": path.as_posix()})
            edges.append({"source": file_id, "target": node_id, "type": "owns", "label": "defines function"})

    for method, route in re.findall(r"@(?:router|app)\.(get|post|put|patch|delete)\(['\"]([^'\"]+)", text):
        node_id = f"api_route:{method.upper()}:{route}"
        nodes.append({"id": node_id, "type": "api_route", "name": f"{method.upper()} {route}", "path": path.as_posix()})
        edges.append({"source": file_id, "target": node_id, "type": "routes_to", "label": "exposes API route"})

    if ".task" in text and "celery" in text.lower():
        for m in re.finditer(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\(", text):
            name = m.group(1)
            node_id = f"worker_task:{path.as_posix()}:{name}"
            nodes.append({"id": node_id, "type": "worker_task", "name": name, "path": path.as_posix()})
            edges.append({"source": file_id, "target": node_id, "type": "owns", "label": "defines worker task"})

    return nodes, edges


def analyze_typescript(path: Path, text: str) -> Tuple[List[dict], List[dict]]:
    nodes, edges = [], []
    file_id = f"file:{path.as_posix()}"

    for m in re.finditer(r"export\s+(?:default\s+)?function\s+([A-Za-z0-9_]+)", text):
        name = m.group(1)
        typ = "frontend_component" if path.suffix == ".tsx" or name[:1].isupper() else "function"
        node_id = f"{typ}:{path.as_posix()}:{name}"
        nodes.append({"id": node_id, "type": typ, "name": name, "path": path.as_posix()})
        edges.append({"source": file_id, "target": node_id, "type": "owns", "label": "exports function/component"})

    for m in re.finditer(r"export\s+(?:const|let)\s+([A-Za-z0-9_]+)", text):
        name = m.group(1)
        typ = "frontend_component" if path.suffix == ".tsx" or name[:1].isupper() else "function"
        node_id = f"{typ}:{path.as_posix()}:{name}"
        nodes.append({"id": node_id, "type": typ, "name": name, "path": path.as_posix()})
        edges.append({"source": file_id, "target": node_id, "type": "owns", "label": "exports symbol"})

    for module in re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", text):
        target_id = f"module:{module}"
        nodes.append({"id": target_id, "type": "module", "name": module, "path": None})
        edges.append({"source": file_id, "target": target_id, "type": "imports", "label": "imports module"})

    return nodes, edges
