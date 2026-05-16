from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy import to avoid startup crash when SEEDANCE_API_KEY is not yet set.
def _get_seedance_config():  # noqa: ANN201
    from app.vendor.seedance2.config import seedance_config  # noqa: PLC0415
    return seedance_config


def _is_seedance_provider(provider: str) -> bool:
    return provider.lower().startswith("seedance")


def _friendly_provider_label(provider: str) -> str:
    key = provider.lower().strip()
    if key in {"seedance2-fast", "seedance2", "seedance"}:
        return "Seedance Fast MVP" if key in {"seedance2-fast", "seedance2"} else "Seedance"
    return provider.replace("_", " ").title()


def _default_seedance_prompt(scene_index: int | None, scene_count: int | None) -> str:
    total = scene_count if isinstance(scene_count, int) and scene_count > 0 else 1
    index = scene_index if isinstance(scene_index, int) and scene_index > 0 else 1
    return (
        "Luxury Korean fashion commercial, cinematic pastel lighting, "
        f"female model walking toward camera, soft cloth motion, dynamic hair movement, "
        f"premium beauty advertising, shallow depth of field, cinematic realism, "
        f"scene {index} of {total}, 9:16"
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SafeSequentialRenderQueue:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict] = {}
        self._lock = threading.RLock()

    def build_execution_steps(self, scene_count: int, planned_batch_size: int, project_id: Optional[str] = None):
        with self._lock:
            if project_id and project_id in self._jobs:
                return list(self._jobs[project_id]["steps"])

        steps = []
        for scene_index in range(1, scene_count + 1):
            steps.append({
                "batch_index": ((scene_index - 1) // planned_batch_size) + 1,
                "scene_index": scene_index,
                "status": "queued",
                "max_concurrent_render": 1,
                "execution_mode": "sequential",
                "provider": "unknown",
                "artifact_path": None,
                "started_at": None,
                "completed_at": None,
                "error": None,
            })
        return steps

    def start_execution(
        self,
        project_id: str,
        scene_count: int,
        planned_batch_size: int,
        provider: str,
        image_url: Optional[str] = None,
        on_event: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        with self._lock:
            existing = self._jobs.get(project_id)
            if existing and existing["status"] == "running":
                return self._snapshot(project_id)

            steps = self.build_execution_steps(scene_count, planned_batch_size)
            for step in steps:
                step["provider"] = provider

            self._jobs[project_id] = {
                "project_id": project_id,
                "provider": provider,
                "status": "running",
                "scene_count": scene_count,
                "planned_batch_size": planned_batch_size,
                "execution_mode": "sequential",
                "max_concurrent_render": 1,
                "started_at": _utc_now(),
                "completed_at": None,
                "image_url": image_url,
                "steps": steps,
            }

            worker = threading.Thread(
                target=self._run_job,
                args=(project_id, on_event),
                daemon=True,
                name=f"creative-os-render-{project_id}",
            )
            worker.start()

            return self._snapshot(project_id)

    def get_status(self, project_id: str) -> Optional[Dict]:
        with self._lock:
            if project_id not in self._jobs:
                return None
            return self._snapshot(project_id)

    def _snapshot(self, project_id: str) -> Dict:
        job = self._jobs[project_id]
        completed = sum(1 for step in job["steps"] if step["status"] == "completed")
        failed = sum(1 for step in job["steps"] if step["status"] == "failed")
        return {
            "project_id": job["project_id"],
            "provider": job["provider"],
            "status": job["status"],
            "scene_count": job["scene_count"],
            "planned_batch_size": job["planned_batch_size"],
            "execution_mode": "sequential",
            "max_concurrent_render": 1,
            "started_at": job["started_at"],
            "completed_at": job["completed_at"],
            "completed_scenes": completed,
            "failed_scenes": failed,
            "steps": list(job["steps"]),
        }

    def _run_job(self, project_id: str, on_event: Optional[Callable[[str], None]]) -> None:
        def emit(message: str) -> None:
            if on_event:
                on_event(message)

        emit(f"Sequential render started for project {project_id}.")

        with self._lock:
            job = self._jobs.get(project_id)
            if not job:
                return

        for step in job["steps"]:
            scene_index = step["scene_index"]
            batch_index = step["batch_index"]
            provider_label = _friendly_provider_label(job["provider"])
            with self._lock:
                step["status"] = "rendering"
                step["started_at"] = _utc_now()
            emit(f"Rendering {provider_label} batch {batch_index}, scene {scene_index}.")

            try:
                artifact_path = self._execute_scene(project_id, step, job)
                with self._lock:
                    step["status"] = "completed"
                    step["artifact_path"] = artifact_path
                    step["completed_at"] = _utc_now()
                emit(f"Completed {provider_label} batch {batch_index}, scene {scene_index}.")
            except Exception as error:  # pragma: no cover - defensive runtime guard
                with self._lock:
                    step["status"] = "failed"
                    step["error"] = str(error)
                    step["completed_at"] = _utc_now()
                    job["status"] = "failed"
                    job["completed_at"] = _utc_now()
                emit(f"Failed {provider_label} batch {batch_index}, scene {scene_index}: {error}")
                return

        with self._lock:
            job["status"] = "completed"
            job["completed_at"] = _utc_now()
        emit(f"Sequential render completed for project {project_id}.")

    def _execute_scene(self, project_id: str, step: Dict, job: Dict) -> str:
        # Runtime execution for each scene. This intentionally runs sequentially
        # (max concurrency = 1) to match provider-safe constraints.
        provider = job["provider"]
        scene_index = step["scene_index"]
        output_dir = Path("artifacts") / "creative_os" / project_id
        output_dir.mkdir(parents=True, exist_ok=True)

        artifact: Dict = {
            "project_id": project_id,
            "scene_index": scene_index,
            "batch_index": step["batch_index"],
            "provider": provider,
            "execution_mode": "sequential",
            "render_status": "completed",
            "rendered_at": _utc_now(),
            "source_image": job.get("image_url"),
        }

        if _is_seedance_provider(provider):
            artifact.update(self._execute_scene_seedance2(step, job))
            if artifact.get("render_status") == "failed":
                raise RuntimeError(str(artifact.get("error") or "Seedance2 render failed"))
        else:
            # Fallback: simulate processing with a deterministic bounded delay.
            time.sleep(0.25)

        artifact_path = output_dir / f"scene_{scene_index:03d}.json"
        artifact_path.write_text(json.dumps(artifact, ensure_ascii=True), encoding="utf-8")
        return str(artifact_path)

    def _execute_scene_seedance2(self, step: Dict, job: Dict) -> Dict:
        """
        Call Bytedance Seedance 2 via kie.ai (backend-only).

        Security contract:
        - API key is read from SEEDANCE_API_KEY (backend env only).
        - This method is called from the backend threading worker.
        - The frontend NEVER calls kie.ai directly.
        - Flow: submit job → get task_id → poll status → return video_url.
        """
        cfg = _get_seedance_config()
        if not cfg.is_configured():
            logger.warning(
                "SEEDANCE_API_KEY not set — scene %s will be simulated.",
                step.get("scene_index"),
            )
            time.sleep(0.25)
            return {"render_status": "simulated", "video_url": None}

        try:
            from app.vendor.seedance2.client import Seedance2Client, Seedance2Error  # noqa: PLC0415
        except ImportError as exc:
            logger.error("seedance2 client not available: %s", exc)
            return {"render_status": "failed", "error": str(exc)}

        # Build prompt from storyboard meta stored on the step (if any).
        prompt: str = (
            step.get("prompt")
            or _default_seedance_prompt(step.get("scene_index"), job.get("scene_count"))
        )
        image_url: Optional[str] = job.get("image_url")
        scene_prompt_meta: Dict = step.get("seedance2_payload") or {}
        aspect_ratio: str = scene_prompt_meta.get("aspect_ratio", "16:9")
        duration: int = scene_prompt_meta.get("duration", 5)
        negative_prompt: str = scene_prompt_meta.get(
            "negative_prompt",
            "morphing, unstable product identity, distorted text, watermark",
        )

        logger.info(
            "%s submit: scene=%s provider=%s base=%s model=%s",
            _friendly_provider_label(cfg.provider_label),
            step.get("scene_index"),
            cfg.provider_label,
            cfg.api_base_url,
            cfg.model,
        )

        try:
            # Seedance2Client reads SEEDANCE_API_KEY / SEEDANCE_API_BASE_URL / SEEDANCE_MODEL
            # from env via SeedanceConfig. No key is passed through the frontend.
            client = Seedance2Client()

            # Step 1: submit → get task_id
            task_id = client.submit_async(
                prompt=prompt,
                image_url=image_url,
                aspect_ratio=aspect_ratio,
                duration=duration,
                negative_prompt=negative_prompt,
            )
            logger.info(
                "%s task submitted: task_id=%s scene=%s",
                _friendly_provider_label(cfg.provider_label),
                task_id,
                step.get("scene_index"),
            )

            # Step 2: poll status until completed / failed
            result = client._poll(task_id, poll_interval=5, timeout=cfg.timeout_seconds)

            # Step 3: extract video_url from response
            result_data = result.get("data") if isinstance(result.get("data"), dict) else {}
            video_url: Optional[str] = (
                result.get("video_url")
                or result.get("output_url")
                or result.get("resultUrl")
                or result_data.get("video_url")
                or result_data.get("output_url")
                or result_data.get("resultUrl")
            )
            logger.info(
                "%s completed: task_id=%s scene=%s video_url=%s",
                _friendly_provider_label(cfg.provider_label),
                task_id,
                step.get("scene_index"),
                video_url,
            )
            return {
                "render_status": "completed",
                "video_url": video_url,
                "task_id": task_id,
                "seedance2_raw": {
                    "status": result.get("status"),
                    "model": result.get("model") or cfg.model,
                    "duration": duration,
                    "provider_label": cfg.provider_label,
                },
            }
        except Exception as exc:  # pragma: no cover - network guard
            logger.exception("%s render failed for scene %s", _friendly_provider_label(cfg.provider_label), step.get("scene_index"))
            return {"render_status": "failed", "error": str(exc)}

safe_render_queue = SafeSequentialRenderQueue()
