"""Drama model training orchestrator — trains all 4 drama ML models.

Calls each drama-engine trainer in sequence (or in parallel via ``--parallel``)
with synthetic data fallback so the pipeline can be validated in CI without a
production DB.  All four models must be trained and registered via env vars
before the PLACEHOLDER Prometheus gauges will drop to 0.

Usage
-----
Train all four models (synthetic data, default output dirs)::

    python -m app.ml.training.drama_train_all

Train with a real DB and non-default artifact root::

    python -m app.ml.training.drama_train_all \\
        --artifact-root /artifacts/models/drama \\
        --db-url postgresql://user:pass@db/brain \\
        --no-synthetic-fallback

Train in parallel (faster on multi-core machines)::

    python -m app.ml.training.drama_train_all --parallel

After training, set env vars and restart API workers::

    DRAMA_TENSION_MODEL_PATH=/artifacts/models/drama/tension/latest.joblib
    DRAMA_INTENT_MODEL_PATH=/artifacts/models/drama/intent/latest.joblib
    DRAMA_SUBTEXT_MODEL_PATH=/artifacts/models/drama/subtext/latest.joblib
    DRAMA_MEMORY_RECALL_MODEL_PATH=/artifacts/models/drama/memory_recall/latest.joblib

Confirm all four Prometheus gauges drop to 0 after workers restart:
    tension_engine_placeholder
    character_intent_engine_placeholder
    subtext_engine_placeholder
    memory_recall_engine_placeholder
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from app.ml.training._runtime_policy import cli_synthetic_fallback_enabled

_logger = logging.getLogger(__name__)

# Mapping: human name → (trainer module attr, default subdir under artifact_root)
_TRAINERS: list[tuple[str, str, str]] = [
    ("tension",      "app.ml.training.drama_tension_trainer",      "tension"),
    ("intent",       "app.ml.training.drama_character_intent_trainer", "intent"),
    ("subtext",      "app.ml.training.drama_subtext_trainer",      "subtext"),
    ("memory_recall","app.ml.training.drama_memory_recall_trainer", "memory_recall"),
]

# Environment variable names to set after training.
_ENV_VAR_MAP: dict[str, str] = {
    "tension":       "DRAMA_TENSION_MODEL_PATH",
    "intent":        "DRAMA_INTENT_MODEL_PATH",
    "subtext":       "DRAMA_SUBTEXT_MODEL_PATH",
    "memory_recall": "DRAMA_MEMORY_RECALL_MODEL_PATH",
}


def _train_one(
    name: str,
    module_path: str,
    artifact_dir: str,
    db_url: str | None,
    synthetic_fallback: bool,
) -> dict[str, Any]:
    """Import and run a single trainer, returning its metrics dict."""
    import importlib  # noqa: PLC0415

    mod = importlib.import_module(module_path)
    metrics: dict[str, Any] = mod.train(
        artifact_dir=artifact_dir,
        db_url=db_url,
        synthetic_fallback=synthetic_fallback,
    )
    return metrics


def train_all(
    artifact_root: str = "/artifacts/models/drama",
    db_url: str | None = None,
    synthetic_fallback: bool = False,
    parallel: bool = False,
    trainers: list[tuple[str, str, str]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Train all four drama models.

    Parameters
    ----------
    artifact_root:
        Root directory under which each model gets its own subdirectory.
        Defaults to ``/artifacts/models/drama``.
    db_url:
        SQLAlchemy database URL.  When ``None`` falls back to ``DATABASE_URL``
        env var.  If still absent, synthetic data is used.
    synthetic_fallback:
        Allow each trainer to fall back to synthetic data when fewer than
        ``min_samples`` labelled rows are available.  Set to ``False`` in
        production to fail hard instead.
    parallel:
        When ``True``, run all four trainers in parallel threads.  Useful on
        multi-core CI agents; set to ``False`` for sequential, easier-to-read
        logs.
    trainers:
        Optional explicit list of ``(name, module_path, subdir)`` tuples to
        train.  Defaults to ``_TRAINERS`` (all four drama models).

    Returns
    -------
    dict
        Mapping ``name → metrics`` for each trained model.
    """
    db_url = db_url or os.getenv("DATABASE_URL", "") or None
    results: dict[str, dict[str, Any]] = {}
    root = Path(artifact_root)

    active_trainers = trainers if trainers is not None else _TRAINERS
    tasks = [
        (name, module, str(root / subdir))
        for name, module, subdir in active_trainers
    ]

    if parallel:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(_train_one, name, module, adir, db_url, synthetic_fallback): name
                for name, module, adir in tasks
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                    _logger.info("drama_train_all: %s done — artifact=%s", name, results[name].get("artifact_path"))
                except Exception as exc:  # noqa: BLE001
                    _logger.error("drama_train_all: %s FAILED — %s", name, exc)
                    results[name] = {"error": str(exc)}
    else:
        for name, module, adir in tasks:
            _logger.info("drama_train_all: training %s …", name)
            try:
                results[name] = _train_one(name, module, adir, db_url, synthetic_fallback)
                _logger.info("drama_train_all: %s done — artifact=%s", name, results[name].get("artifact_path"))
            except Exception as exc:  # noqa: BLE001
                _logger.error("drama_train_all: %s FAILED — %s", name, exc)
                results[name] = {"error": str(exc)}

    return results


def _print_env_export(results: dict[str, dict[str, Any]]) -> None:
    """Print shell export commands for all successfully trained models."""
    print("\n# ── Set these env vars and restart API workers ─────────────────────")
    for name, metrics in results.items():
        if "error" in metrics:
            print(f"# ERROR: {name} training failed — {metrics['error']}")
            continue
        artifact_path = metrics.get("artifact_path", "")
        env_var = _ENV_VAR_MAP.get(name, f"DRAMA_{name.upper()}_MODEL_PATH")
        print(f"export {env_var}={artifact_path}")
    print(
        "# After restart, confirm Prometheus gauges drop to 0:\n"
        "#   tension_engine_placeholder\n"
        "#   character_intent_engine_placeholder\n"
        "#   subtext_engine_placeholder\n"
        "#   memory_recall_engine_placeholder\n"
        "# ──────────────────────────────────────────────────────────────────────"
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
    parser = argparse.ArgumentParser(
        description="Train all four drama ML models (tension, intent, subtext, memory_recall)."
    )
    parser.add_argument(
        "--artifact-root",
        default="/artifacts/models/drama",
        help="Root directory for model artifacts (default: /artifacts/models/drama)",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="SQLAlchemy DB URL (defaults to DATABASE_URL env var)",
    )
    parser.add_argument(
        "--no-synthetic-fallback",
        action="store_true",
        help="Fail hard when fewer than min_samples labelled rows are found (forced on in production/staging)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run trainers in parallel threads (faster on multi-core machines)",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=["tension", "intent", "subtext", "memory_recall"],
        default=None,
        help="Train only the listed models (default: all four)",
    )
    args = parser.parse_args()

    # Filter trainers if --only was specified.
    trainers_to_run = _TRAINERS
    if args.only:
        trainers_to_run = [(n, m, s) for n, m, s in _TRAINERS if n in args.only]

    synthetic_fallback = cli_synthetic_fallback_enabled(
        no_synthetic_fallback=args.no_synthetic_fallback
    )

    results = train_all(
        artifact_root=args.artifact_root,
        db_url=args.db_url,
        synthetic_fallback=synthetic_fallback,
        parallel=args.parallel,
        trainers=trainers_to_run,
    )

    print(json.dumps(results, indent=2, default=str))
    _print_env_export(results)

    failures = [name for name, m in results.items() if "error" in m]
    if failures:
        _logger.error("drama_train_all: %d trainer(s) failed: %s", len(failures), failures)
        sys.exit(1)


if __name__ == "__main__":
    main()
