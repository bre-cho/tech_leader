from .schemas import FashionRuntimeRequest, FashionRuntimeResponse, SequentialRenderStep
from .visual_dna_extractor import visual_dna_extractor
from .emotional_perception_graph import emotional_perception_graph_builder
from .character_continuity_runtime import character_continuity_runtime
from .fashion_motion_engine import fashion_motion_engine
from .beauty_commerce_engine import beauty_commerce_engine
from .storyboard_runtime import fashion_storyboard_runtime
from .winner_dna_memory import winner_dna_memory_builder


class FashionBeautyRuntimeOrchestrator:
    def analyze(self, request: FashionRuntimeRequest) -> FashionRuntimeResponse:
        dna = visual_dna_extractor.extract(request.brief)
        emotional_graph = emotional_perception_graph_builder.build(dna)
        continuity = character_continuity_runtime.build(dna)
        motion = fashion_motion_engine.build(dna)
        commerce = beauty_commerce_engine.build(dna, emotional_graph)
        storyboard = fashion_storyboard_runtime.build(
            brief=request.brief,
            dna=dna,
            continuity=continuity,
            motion=motion,
            target_duration=request.target_duration,
            provider=request.provider,
        )

        render_steps = [
            SequentialRenderStep(
                batch_index=((scene.scene_index - 1) // request.planned_batch_size) + 1,
                scene_index=scene.scene_index,
                status="queued",
                max_concurrent_render=1,
                execution_mode="sequential",
            )
            for scene in storyboard
        ]

        winner_memory = winner_dna_memory_builder.build(dna, commerce, motion, request.provider)

        return FashionRuntimeResponse(
            brief=request.brief,
            visual_dna=dna,
            emotional_graph=emotional_graph,
            continuity_lock=continuity,
            fashion_motion=motion,
            beauty_commerce=commerce,
            storyboard=storyboard,
            sequential_render_plan=render_steps,
            winner_dna_memory=winner_memory,
        )


fashion_beauty_runtime_orchestrator = FashionBeautyRuntimeOrchestrator()
