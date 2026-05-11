from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import uuid

from .artifact_storage_service import LocalArtifactStorageService
from .contracts import ArtifactContract, FinalVideoContract, RenderProductionError, ensure_file, write_json
from .ffmpeg_utils import assert_aspect_ratio, audio_stream_info, get_duration, video_stream_info
from .final_video_assembly_service import FinalVideoAssemblyService
from .real_audio_mix_service import RealAudioMixService
from .real_subtitle_burn_service import RealSubtitleBurnService


class ProductionRenderOrchestrator:
    """Turns a RenderPackage plan into a real final.mp4.

    RenderPackage = kế hoạch. Orchestrator này là runtime sản xuất file cuối.
    """

    def __init__(
        self,
        *,
        work_root: str | Path = "./storage/render_work",
        storage: Optional[LocalArtifactStorageService] = None,
    ):
        self.work_root = Path(work_root)
        self.storage = storage or LocalArtifactStorageService()
        self.assembler = FinalVideoAssemblyService()
        self.audio = RealAudioMixService()
        self.subtitle = RealSubtitleBurnService()

    def execute(
        self,
        *,
        render_package: Dict[str, Any],
        scene_video_paths: Iterable[str],
        voice_audio_path: Optional[str] = None,
        bgm_path: Optional[str] = None,
        sfx_paths: Optional[Iterable[str]] = None,
        subtitle_path: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        contract = self.execute_contract(
            render_package=render_package,
            scene_video_paths=scene_video_paths,
            voice_audio_path=voice_audio_path,
            bgm_path=bgm_path,
            sfx_paths=sfx_paths,
            subtitle_path=subtitle_path,
            job_id=job_id,
        )
        return contract.to_dict()

    def execute_contract(
        self,
        *,
        render_package: Dict[str, Any],
        scene_video_paths: Iterable[str],
        voice_audio_path: Optional[str] = None,
        bgm_path: Optional[str] = None,
        sfx_paths: Optional[Iterable[str]] = None,
        subtitle_path: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> FinalVideoContract:
        job = job_id or render_package.get("job_id") or f"render_{uuid.uuid4().hex[:12]}"
        work = self.work_root / job
        work.mkdir(parents=True, exist_ok=True)
        timeline: List[Dict[str, Any]] = []

        scene_paths = [str(ensure_file(p, "scene video")) for p in scene_video_paths]
        if len(scene_paths) < 1:
            raise RenderProductionError("NO_SCENE_VIDEO -> NO_FINAL_RENDER")
        timeline.append({"step": "input_scenes", "count": len(scene_paths)})
        output_cfg = render_package.get("output_config", {}) or render_package.get("campaign_brief", {}) or {}
        width = int(output_cfg.get("width") or 1080)
        height = int(output_cfg.get("height") or 1920)
        fps = int(output_cfg.get("fps") or output_cfg.get("frame_rate") or 30)

        raw_video = str(work / "final_raw_no_audio.mp4")
        self.assembler.assemble(scene_video_paths=scene_paths, output_path=raw_video, work_dir=str(work), width=width, height=height, fps=fps)
        timeline.append({"step": "assemble", "path": raw_video, "duration": get_duration(raw_video)})

        mixed_audio = None
        if voice_audio_path:
            mixed_audio = str(work / "final_audio.m4a")
            self.audio.mix(voice_path=voice_audio_path, bgm_path=bgm_path, sfx_paths=sfx_paths or [], output_path=mixed_audio)
            timeline.append({"step": "audio_mix", "path": mixed_audio, "duration": get_duration(mixed_audio)})
        elif subtitle_path:
            raise RenderProductionError("NO_VOICE_AUDIO -> NO_SUBTITLE_BURN_FOR_KARAOKE")

        final_path = str(work / "final.mp4")
        self.subtitle.burn(video_path=raw_video, audio_path=mixed_audio, subtitle_path=subtitle_path, output_path=final_path)
        timeline.append({"step": "subtitle_burn_mux", "path": final_path, "duration": get_duration(final_path)})

        quality_gate = self._quality_gate(final_path=final_path, scene_count=len(scene_paths), subtitle_path=subtitle_path, audio_path=mixed_audio)
        if quality_gate["status"] != "PASS":
            raise RenderProductionError(f"FINAL_QUALITY_GATE_FAIL: {quality_gate}")

        scene_contracts: List[ArtifactContract] = []
        for idx, p in enumerate(scene_paths, start=1):
            scene_contracts.append(self.storage.put_file(source_path=p, artifact_type="scene_video", source_job_id=job, source_scene_id=f"scene_{idx:03d}", metadata={"index": idx}))

        audio_contract = self.storage.put_file(source_path=mixed_audio, artifact_type="final_audio", source_job_id=job) if mixed_audio else None
        subtitle_contract = self.storage.put_file(source_path=subtitle_path, artifact_type="subtitle", source_job_id=job) if subtitle_path else None
        parent_ids = [a.artifact_id for a in scene_contracts]
        if audio_contract:
            parent_ids.append(audio_contract.artifact_id)
        if subtitle_contract:
            parent_ids.append(subtitle_contract.artifact_id)
        final_contract = self.storage.put_file(source_path=final_path, artifact_type="final_video", source_job_id=job, parent_artifact_ids=parent_ids, metadata={"render_package_id": render_package.get("render_package_id") or render_package.get("storyboard_id")})

        result = FinalVideoContract(
            job_id=job,
            status="completed",
            final_video=final_contract,
            thumbnail=None,
            scene_artifacts=scene_contracts,
            audio_artifact=audio_contract,
            subtitle_artifact=subtitle_contract,
            quality_gate=quality_gate,
            timeline=timeline,
        )
        write_json(work / "final_contract.json", result.to_dict())
        return result

    def _quality_gate(self, *, final_path: str, scene_count: int, subtitle_path: Optional[str], audio_path: Optional[str]) -> Dict[str, Any]:
        ensure_file(final_path, "final video")
        v = video_stream_info(final_path)
        a = audio_stream_info(final_path)
        duration = get_duration(final_path)
        checks = {
            "file_exists": True,
            "size_bytes_gt_0": Path(final_path).stat().st_size > 0,
            "scene_count_gt_0": scene_count > 0,
            "duration_gt_0": duration > 0,
            "has_video_stream": bool(v),
            "has_audio_stream": bool(a) if audio_path else True,
            "subtitle_file_present": bool(subtitle_path) if subtitle_path else True,
        }
        try:
            assert_aspect_ratio(final_path, "9:16")
            checks["aspect_ratio_9_16"] = True
        except Exception as e:
            checks["aspect_ratio_9_16"] = False
            checks["aspect_ratio_error"] = str(e)
        return {
            "status": "PASS" if all(v is True for k, v in checks.items() if not k.endswith("_error")) else "FAIL",
            "checks": checks,
            "duration_seconds": duration,
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
        }
