
from __future__ import annotations

from .schemas import CodeGraphEdge, CodeGraphNode


PRODUCTION_STEPS = [
    ("pipeline:input", "Input Poster / Brief", "poster-to-storyboard", "User uploads poster/image/campaign brief/JSON idea."),
    ("pipeline:code_graph", "Code Intelligence Graph", "code-intelligence", "Map active modules and available paths before orchestration."),
    ("pipeline:storyboard", "Storyboard Engine", "storyboard-engine", "Analyze poster/brief, detect mechanism, generate scenes, shots and camera plan."),
    ("pipeline:multi_angle", "Single Image Multi-Angle", "multi-angle-storyboard", "Generate all camera angles from one input image when needed."),
    ("pipeline:higgsfield_seedance2", "Higgsfield × Seedance2 Optimizer", "higgsfield-seedance2", "Apply 2-second hook, camera grammar and Seedance motion prompts."),
    ("pipeline:provider_payload", "Provider Payload Compiler", "multi-provider", "Compile Veo/Runway/Kling/Seedance provider payloads per scene."),
    ("pipeline:provider_render", "Provider Render Dispatch", "multi-provider", "Dispatch and poll AI video provider jobs."),
    ("pipeline:html_render", "HTML Motion Render", "html-render", "Render deterministic HTML motion scenes via Playwright when suitable."),
    ("pipeline:audio", "Audio Engine", "audio-engine", "Generate narration/voice clone/BGM/SFX and mix audio."),
    ("pipeline:avatar", "Avatar Engine", "avatar-engine", "Optional presenter/avatar generation and continuity control."),
    ("pipeline:drama", "Drama Engine", "drama-engine", "Enhance emotion/tension/reveal/pacing for the video."),
    ("pipeline:subtitle", "Smart Subtitle Engine", "smart-subtitle", "Generate karaoke ASS/SRT, safe zones and burn plan."),
    ("pipeline:assembly", "Production Render Assembly", "production-render", "FFmpeg concat, mux, subtitle burn and final.mp4 export."),
    ("pipeline:artifact", "Artifact Contract", "artifact-contracts", "Validate, store and expose final video contract."),
    ("pipeline:analytics", "AI Video Factory Feedback", "ai-video-factory", "Collect analytics, A/B hooks, viral score, RL loop and optimization memory."),
]


def build_pipeline_nodes_and_edges() -> tuple[list[CodeGraphNode], list[CodeGraphEdge]]:
    nodes = [
        CodeGraphNode(
            id=sid,
            type="pipeline_step",
            name=name,
            layer="closed-loop-production-pipeline",
            domain=domain,
            summary=summary,
            metadata={"order": idx},
        )
        for idx, (sid, name, domain, summary) in enumerate(PRODUCTION_STEPS, start=1)
    ]

    edges: list[CodeGraphEdge] = []
    for idx in range(len(PRODUCTION_STEPS) - 1):
        edges.append(
            CodeGraphEdge(
                source=PRODUCTION_STEPS[idx][0],
                target=PRODUCTION_STEPS[idx + 1][0],
                type="next_step",
                label="closed-loop next step",
                metadata={"order": idx + 1},
            )
        )

    # Optional branches and fallbacks.
    edges += [
        CodeGraphEdge(source="pipeline:provider_payload", target="pipeline:html_render", type="fallback_to", label="use HTML motion when provider is unnecessary or too expensive"),
        CodeGraphEdge(source="pipeline:storyboard", target="pipeline:drama", type="requires", label="drama engine can improve weak pacing before render"),
        CodeGraphEdge(source="pipeline:storyboard", target="pipeline:avatar", type="requires", label="avatar is required for presenter/talking-head workflows"),
        CodeGraphEdge(source="pipeline:assembly", target="pipeline:subtitle", type="requires", label="subtitle burn requires subtitle artifact"),
        CodeGraphEdge(source="pipeline:analytics", target="pipeline:storyboard", type="fallback_to", label="feedback loop mutates future storyboard hooks"),
    ]

    return nodes, edges
