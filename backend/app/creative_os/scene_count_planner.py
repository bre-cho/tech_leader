from math import ceil

from .provider_duration_profiles import get_provider_profile
from .schemas import RenderBatch, StoryboardPlan, StoryboardPlanRequest, StoryboardScene

CAMERA_LIBRARY = [
    ("Hook Scene", "slow push-in", "cinematic glide", "Open with attention"),
    ("Product Focus", "macro beauty shot", "soft rotation", "Show product details"),
    ("Desire Scene", "portrait close-up", "slow zoom", "Build desire"),
    ("Trust Scene", "medium shot", "light drift", "Increase trust"),
    ("Transformation", "smooth reveal", "before-after motion", "Show transformation"),
    ("CTA Scene", "front hero shot", "logo reveal", "Call to action"),
]


def _scene(index: int, duration: float, provider: str) -> StoryboardScene:
    title, camera, motion, subtitle = CAMERA_LIBRARY[(index - 1) % len(CAMERA_LIBRARY)]
    return StoryboardScene(
        index=index,
        title=title,
        camera=camera,
        motion=motion,
        subtitle=subtitle,
        provider=provider,
        duration=round(duration, 2),
        continuity_key=f"continuity_scene_{index:02d}",
    )


def plan_storyboard(project_id: str, request: StoryboardPlanRequest) -> StoryboardPlan:
    profile = get_provider_profile(request.provider)
    scene_count = max(1, ceil(request.target_video_duration / profile.recommended_duration_per_scene))
    scene_duration = request.target_video_duration / scene_count
    planned_batch_size = max(1, request.planned_batch_size or profile.default_planned_batch_size)

    scenes = [_scene(i, scene_duration, profile.provider) for i in range(1, scene_count + 1)]
    all_scene_indexes = list(range(1, scene_count + 1))
    chunks = [
        all_scene_indexes[i : i + planned_batch_size]
        for i in range(0, scene_count, planned_batch_size)
    ]
    batches = [
        RenderBatch(
            batch_index=i + 1,
            scene_indexes=chunk,
            planned_batch_size=planned_batch_size,
            max_concurrent_render=1,
        )
        for i, chunk in enumerate(chunks)
    ]

    return StoryboardPlan(
        project_id=project_id,
        image_source=request.image_source,
        image_url=request.image_url,
        target_video_duration=request.target_video_duration,
        provider=profile.provider,
        recommended_duration_per_scene=profile.recommended_duration_per_scene,
        scene_count=scene_count,
        scene_duration=round(scene_duration, 2),
        planned_batch_size=planned_batch_size,
        max_concurrent_render=1,
        total_batches=len(batches),
        execution_mode="sequential",
        scenes=scenes,
        batches=batches,
    )
