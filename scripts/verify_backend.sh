#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
python -m compileall app
PYTHONPATH=. pytest -q
