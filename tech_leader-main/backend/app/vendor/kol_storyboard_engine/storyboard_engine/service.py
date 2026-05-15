from __future__ import annotations

import concurrent.futures
import os
from typing import Any

from .mechanism_detector import VisualMechanismDetector
from .poster_analyzer import PosterAnalyzer
from .schemas import PosterInput, StoryboardResponse
from .storyboard_generator import StoryboardGenerator

_STORYBOARD_GENERATOR_TIMEOUT_SECONDS: float = float(
    os.environ.get("STORYBOARD_GENERATOR_TIMEOUT_SECONDS", "60")
)


class AutoStoryboardService:
    def __init__(self) -> None:
        self.poster_analyzer = PosterAnalyzer()
        self.mechanism_detector = VisualMechanismDetector()
        self.generator = StoryboardGenerator()

    def _generate_variant(self, brief: Any, visual: Any, mechanism: Any, variant: Any, providers: Any) -> Any:
        """Generate a single storyboard variant with timeout enforcement.

        Runs in a thread-pool executor so the calling thread is not blocked
        indefinitely when the underlying LLM/generator is slow or hangs.
        """
        timeout = _STORYBOARD_GENERATOR_TIMEOUT_SECONDS
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self.generator.generate, brief, visual, mechanism, variant, providers
            )
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(
                    f"Storyboard generator timed out after {timeout}s for variant={variant}. "
                    "Increase STORYBOARD_GENERATOR_TIMEOUT_SECONDS or investigate generator latency."
                )

    def run(self, payload: PosterInput) -> StoryboardResponse:
        brief = payload.campaign_brief
        visual = self.poster_analyzer.analyze(
            brief=brief,
            poster_image_url=str(payload.poster_image_url) if payload.poster_image_url else None,
            poster_image_base64=payload.poster_image_base64,
        )
        mechanism = self.mechanism_detector.detect(brief, visual)
        storyboards = [
            self._generate_variant(brief, visual, mechanism, variant, payload.providers)
            for variant in payload.requested_variants
        ]
        recommended = sorted(storyboards, key=lambda s: s.scorecard.final_score, reverse=True)[0].variant
        export_ready = all(s.scorecard.final_score >= 75 for s in storyboards)
        return StoryboardResponse(storyboards=storyboards, recommended_variant=recommended, export_ready=export_ready)
