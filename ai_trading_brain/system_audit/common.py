
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Iterable, Optional
import json, ast, re, hashlib, time, os

STATUS_PASS='PASS'; STATUS_WARN='WARN'; STATUS_FAIL='FAIL'

def read_text_safe(path: Path) -> str:
    try: return path.read_text(encoding='utf-8')
    except UnicodeDecodeError: return path.read_text(encoding='latin-1', errors='ignore')
    except Exception: return ''

def rel(path: Path, root: Path) -> str:
    try: return str(path.relative_to(root)).replace('\\','/')
    except Exception: return str(path)

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    try: h.update(path.read_bytes())
    except Exception: pass
    return h.hexdigest()

def py_files(root: Path) -> List[Path]:
    return [p for p in root.rglob('*.py') if '__pycache__' not in p.parts and '.venv' not in p.parts]

def all_code_files(root: Path) -> List[Path]:
    exts={'.py','.ts','.tsx','.js','.jsx','.json','.yaml','.yml','.md','.toml'}
    return [p for p in root.rglob('*') if p.is_file() and p.suffix in exts and '__pycache__' not in p.parts]
