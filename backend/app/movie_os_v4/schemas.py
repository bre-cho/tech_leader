from typing import Dict, List, Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class MovieOSV4Request(BaseModel):
    prompt: str
    target_duration: float = Field(default=60, gt=0)
    provider: str = "kling"
    planned_batch_size: int = 6
    max_concurrent_render: int = 1
    memory_namespace: str = "default_movie_os"

    @field_validator("max_concurrent_render")
    @classmethod
    def force_sequential(cls, value: int) -> int:
        return 1


class AIDirectorBrief(BaseModel):
    logline: str
    genre: str
    audience_emotion: str
    visual_promise: str
    director_intent: str
    success_criteria: List[str]


class NarrativeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    role: str
    description: str
    weight: float


class NarrativeGraph(BaseModel):
    nodes: List[NarrativeNode]
    edges: List[Dict[str, str]]


class MoodColorLensProfile(BaseModel):
    mood: str
    secondary_moods: List[str]
    lighting: str
    lens: str
    color_script: List[str]
    texture_language: List[str]
    transition_language: List[str]
    soundtrack_direction: str


class CharacterBible(BaseModel):
    identity_lock: str
    face: str
    costume: str
    jewelry: str
    hairstyle: str
    age: str
    body_silhouette: str
    makeup: str
    continuity_rules: List[str]


class ShotPlanItem(BaseModel):
    scene_index: int
    title: str
    shot_role: str
    camera_move: str
    lens: str
    framing: str
    motion: str
    emotion: str
    duration: float
    provider: str


class EmotionalTimelinePoint(BaseModel):
    scene_index: int
    emotional_state: str
    tension: int
    visual_density: int
    retention_goal: str
    silence_or_breath: str


class EmotionalTimelineGraph(BaseModel):
    total_duration: float
    peak_scene_index: int
    points: List[EmotionalTimelinePoint]


class StoryboardScene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scene_index: int
    title: str
    visual_prompt: str
    negative_prompt: str
    camera_move: str
    lens: str
    lighting: str
    color_script: List[str]
    duration: float
    provider: str
    continuity_hash: str


class SceneDependency(BaseModel):
    source_scene: int
    target_scene: int
    dependency_type: str
    rebuild_policy: str


class SceneDependencyGraph(BaseModel):
    dependencies: List[SceneDependency]


class SequentialRenderStep(BaseModel):
    batch_index: int
    scene_index: int
    status: str = "queued"
    max_concurrent_render: int = 1
    execution_mode: str = "sequential"


class SequentialRuntimePlan(BaseModel):
    provider: str
    planned_batch_size: int
    max_concurrent_render: int = 1
    execution_mode: str = "sequential"
    steps: List[SequentialRenderStep]


class AIEditorPlan(BaseModel):
    edit_style: str
    transitions: List[str]
    pacing_rules: List[str]
    sound_design: List[str]
    subtitle_strategy: str
    color_grade: str


class FinalMovieAssemblyPlan(BaseModel):
    tracks: List[str]
    artifact_targets: List[str]
    export_profiles: List[str]
    final_duration: float


class MemoryGraphUpdate(BaseModel):
    namespace: str
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]
    winner_dna: Dict[str, str]


class MovieOSV4Response(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str
    director_brief: AIDirectorBrief
    narrative_graph: NarrativeGraph
    mood_profile: MoodColorLensProfile
    character_bible: CharacterBible
    shot_plan: List[ShotPlanItem]
    emotional_timeline: EmotionalTimelineGraph
    storyboard: List[StoryboardScene]
    scene_dependency_graph: SceneDependencyGraph
    sequential_runtime_plan: SequentialRuntimePlan
    editor_plan: AIEditorPlan
    assembly_plan: FinalMovieAssemblyPlan
    memory_update: MemoryGraphUpdate


class SceneRebuildRequest(BaseModel):
    scene_index: int
    reason: str
    dependency_policy: Literal[
        "rebuild_scene_only",
        "rebuild_scene_and_following",
        "rebuild_dependency_range",
    ] = "rebuild_scene_only"


class SceneRebuildPlan(BaseModel):
    scene_index: int
    reason: str
    affected_scenes: List[int]
    dependency_policy: str
    max_concurrent_render: int = 1
    execution_mode: str = "sequential"
