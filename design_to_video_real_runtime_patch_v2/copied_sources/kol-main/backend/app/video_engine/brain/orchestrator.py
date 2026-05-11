from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from .contracts import BrainPlan
from .learning_loop import LearningLoopStore
from .prompt_compiler import PromptCompiler
from .provider_decision_engine import ProviderDecisionEngine

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class VideoBrainOrchestrator:
    def __init__(
        self,
        compiler: PromptCompiler | None = None,
        decision_engine: ProviderDecisionEngine | None = None,
        learning_store: LearningLoopStore | None = None,
        db: "Session | None" = None,
    ):
        # db is forwarded to LearningLoopStore so the DB backend is used in
        # production (file backend raises RuntimeError when is_production_env()
        # is True and no db session is provided).
        self.learning_store = learning_store or LearningLoopStore(db=db)
        self.compiler = compiler or PromptCompiler()
        self.decision_engine = decision_engine or ProviderDecisionEngine(learning_store=self.learning_store)

    def plan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        intent = self.compiler.build_intent(request)
        decision = self.decision_engine.decide(
            intent,
            requested_provider=request.get("provider", "auto"),
            routing_profile=request.get("routing_profile", "cinematic_ads"),
        )
        payload = self.compiler.compile_for_provider(intent, decision.selected_provider, decision.selected_model)
        plan = BrainPlan(
            intent=intent,
            selected_provider=decision.selected_provider,
            selected_model=decision.selected_model,
            decision_reason=decision.decision_reason,
            fallback_chain=decision.fallback_chain,
            compiled_payload=payload,
            rejected=decision.rejected,
            scorecard=decision.scorecard,
        )
        return plan.model_dump(mode="json")

    def record_outcome(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        return self.learning_store.record_outcome(outcome)
