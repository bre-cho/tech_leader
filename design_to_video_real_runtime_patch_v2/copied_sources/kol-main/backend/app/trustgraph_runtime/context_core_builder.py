
from __future__ import annotations
from uuid import uuid4
from .schemas import ContextCore, ContextGraphEdge, ContextGraphNode, ProvenanceRef

def _prov(path: str, note: str = ""):
    return [ProvenanceRef(source_type="code", source_path=path, confidence=0.95, note=note)]

def build_video_factory_context_core() -> ContextCore:
    nodes, edges = [], []

    _schemas_path = "backend/app/trustgraph_runtime/schemas.py"
    _builder_path = "backend/app/trustgraph_runtime/context_core_builder.py"

    def node(id, typ, name, domain, summary, path="", schema=None, meta=None):
        nodes.append(ContextGraphNode(
            id=id, type=typ, name=name, domain=domain, summary=summary,
            payload_schema=schema or {}, metadata=meta or {},
            provenance=_prov(path, summary) if path else []
        ))

    def edge(src, dst, typ, label, policy=None, path=""):
        edges.append(ContextGraphEdge(
            source=src, target=dst, type=typ, label=label, policy=policy or {},
            provenance=_prov(path, label) if path else []
        ))

    # Contracts — provenance references the schemas module that defines each contract shape.
    node("contract:input","data_contract","InputContract","contracts","Poster image, campaign brief, platform, duration and provider preference.", _schemas_path)
    node("contract:storyboard","data_contract","StoryboardContract","contracts","Scene list, time ranges, goals, visual/camera/audio plan.", _schemas_path)
    node("contract:render_package","data_contract","RenderPackageContract","contracts","Provider payloads, scene render plan, audio/subtitle plan and hard rules.", _schemas_path)
    node("contract:scene_artifacts","data_contract","SceneArtifactsContract","contracts","Rendered scene videos or deterministic HTML motion outputs.", _schemas_path)
    node("contract:audio","data_contract","AudioContract","contracts","Voice, BGM, SFX, mixed audio and word timing metadata.", _schemas_path)
    node("contract:subtitle","data_contract","SubtitleContract","contracts","ASS/SRT, karaoke timing, safe-zone placement and burn filter.", _schemas_path)
    node("contract:final_video","data_contract","FinalVideoContract","contracts","Final mp4 URL/path, checksum, duration, aspect ratio, artifact manifest.", _schemas_path)

    modules = [
        ("module:poster_analyzer","Poster Analyzer","poster-to-storyboard","Analyze poster/brief into visual mechanism and direction.","backend/app/storyboard_engine"),
        ("module:storyboard_engine","Storyboard Engine","storyboard-engine","Generate scenes, camera plan, voiceover, render handoff.","backend/app/storyboard_engine"),
        ("module:cinematic_language_engine","Cinematic Language Engine","cinematic-language-engine","Apply camera technique grammar, lens psychology and provider-ready cinematic prompts.","backend/app/cinematic_language_engine"),
        ("module:multi_angle","Single Image Multi-Angle Engine","multi-angle-storyboard","Infer multiple cinematic camera angles from one source image.","backend/app/storyboard_production/multi_angle_engine"),
        ("module:higgsfield_seedance2","Higgsfield Seedance2 Optimizer","higgsfield-seedance2","Apply 2-second hook, camera grammar, Seedance prompt quality gate.","backend/app/higgsfield_seedance2_engine"),
        ("module:provider_router","Multi Provider Router","multi-provider","Compile and route scene prompts to Veo, Runway, Kling, Seedance2 or fallback.","backend/app/providers"),
        ("module:html_render","HTML Motion Renderer","html-render","Deterministic Playwright capture path for motion graphics and news scenes.","backend/app/services"),
        ("module:audio_engine","Audio Engine","audio-engine","Create narration, voice clone, BGM/SFX and mixed track.","backend/app/audio"),
        ("module:avatar_engine","Avatar Engine","avatar-engine","Optional presenter/avatar generation and continuity.","backend/app/avatar"),
        ("module:drama_engine","Drama Engine","drama-engine","Improve hook, pacing, tension, reveal and emotional arc.","backend/app/drama"),
        ("module:smart_subtitle","Smart Subtitle Engine","smart-subtitle","Generate karaoke ASS/SRT, safe-zone subtitle layout and burn plan.","backend/app/smart_subtitle_engine"),
        ("module:production_render","Production Render Orchestrator","production-render","FFmpeg scene concat, audio mux, subtitle burn and final mp4 export.","backend/app/services/render_production"),
        ("module:artifact_storage","Artifact Storage","artifact-contracts","Store and validate generated artifacts and final video contract.","backend/app/services"),
        ("module:analytics_feedback","AI Video Factory Feedback","ai-video-factory","Analytics, A/B hook, thumbnail mutation, RL memory and viral optimization.","backend/app/ai_video_factory"),
    ]
    for item in modules:
        node(item[0], "module", item[1], item[2], item[3], item[4])

    policies = [
        ("policy:no_storyboard_no_render","NO_STORYBOARD -> NO_RENDER_PACKAGE"),
        ("policy:no_provider_payload_no_scene_render","NO_PROVIDER_PAYLOAD_AND_NO_HTML_SCENE -> NO_SCENE_RENDER"),
        ("policy:no_audio_no_final","NO_AUDIO -> NO_FINAL_EXPORT"),
        ("policy:no_subtitle_safe_zone_no_burn","NO_SUBTITLE_SAFE_ZONE -> NO_BURN_IN"),
        ("policy:no_final_contract_no_download","NO_FINAL_VIDEO_CONTRACT -> NO_DOWNLOAD"),
        ("policy:provenance_required","Every final artifact must include source scene/module provenance."),
    ]
    for pid, summary in policies:
        node(pid, "policy", pid.replace("policy:",""), "policy", summary, _builder_path)

    # Closed-loop edges
    edge("contract:input","module:poster_analyzer","consumes","Poster analyzer consumes input.")
    edge("module:poster_analyzer","module:storyboard_engine","next_step","Visual mechanism informs storyboard.")
    edge("module:storyboard_engine","contract:storyboard","produces","Storyboard engine produces StoryboardContract.")
    edge("contract:storyboard","module:cinematic_language_engine","consumes","Cinematic language engine consumes storyboard intent and campaign brief.")
    edge("module:cinematic_language_engine","contract:storyboard","produces","Cinematic-enriched storyboard and provider prompt grammar.")
    edge("contract:storyboard","module:multi_angle","consumes","Multi-angle can augment storyboard when source image exists.")
    edge("module:multi_angle","contract:storyboard","produces","Multi-angle scenes are appended to storyboard.")
    edge("contract:storyboard","module:avatar_engine","consumes","Avatar engine uses storyboard timeline to schedule presenter segments.", {"optional": True})
    edge("module:avatar_engine","contract:scene_artifacts","produces","Avatar engine contributes presenter/avatar segments to scene artifacts.", {"optional": True})
    edge("contract:storyboard","module:drama_engine","consumes","Drama engine improves weak hook/pacing.")
    edge("module:drama_engine","contract:storyboard","produces","Drama-enhanced storyboard.")
    edge("contract:storyboard","module:higgsfield_seedance2","consumes","Seedance optimizer consumes scenes and camera plan.")
    edge("module:higgsfield_seedance2","module:provider_router","next_step","Optimized prompts flow to provider router.")
    edge("module:cinematic_language_engine","module:provider_router","next_step","Cinematic prompt compiler feeds provider router payload preparation.")
    edge("module:provider_router","contract:render_package","produces","Provider router produces RenderPackageContract.")
    edge("contract:render_package","module:provider_router","consumes","Provider render consumes provider payloads.")
    edge("module:provider_router","contract:scene_artifacts","produces","Provider jobs produce scene artifacts.", {"allow_partial": True})
    edge("module:provider_router","module:html_render","fallback_to","Fallback to deterministic HTML motion render.", {"when":"provider_failed_or_disabled"})
    edge("module:html_render","contract:scene_artifacts","produces","HTML render produces scene video artifacts.")
    edge("contract:storyboard","module:audio_engine","consumes","Audio engine consumes voiceover/script plan.")
    edge("module:audio_engine","contract:audio","produces","Audio engine produces mixed audio.")
    edge("contract:audio","module:smart_subtitle","consumes","Smart subtitle uses audio/word timing.")
    edge("module:smart_subtitle","contract:subtitle","produces","Subtitle engine produces ASS/SRT/burn plan.")
    edge("contract:scene_artifacts","module:production_render","consumes","Production render consumes scene videos.")
    edge("contract:audio","module:production_render","consumes","Production render consumes mixed audio.")
    edge("contract:subtitle","module:production_render","consumes","Production render consumes subtitle burn plan.")
    edge("module:production_render","contract:final_video","produces","Production render outputs final video contract.")
    edge("contract:final_video","module:artifact_storage","validates","Artifact storage validates checksum, mime, size, duration.")
    edge("contract:final_video","module:analytics_feedback","next_step","Analytics feedback begins after publish.", {"post_publish": True})
    for pid, _ in policies:
        edge(pid, "contract:final_video", "controlled_by", "Final contract is controlled by hard production policy.")

    return ContextCore(
        core_id=f"video_factory_context_core_{uuid4().hex[:10]}",
        version="v1",
        name="Poster to Render Video Context Core",
        description="Portable TrustGraph-inspired context core for closed-loop AI video production.",
        nodes=nodes,
        edges=edges,
        retrieval_policies={
            "entry_points": ["contract:input","module:storyboard_engine","module:production_render","contract:final_video"],
            "prefer_domains": ["contracts","storyboard-engine","multi-provider","production-render","artifact-contracts"],
            "require_provenance": True,
            "traversal_depth": 3,
        },
        promotion_policy={
            "final_video_contract_required": True,
            "artifact_checksum_required": True,
            "scene_artifact_required": True,
            "audio_required": True,
            "subtitle_required_for_social_video": True,
        },
    )
