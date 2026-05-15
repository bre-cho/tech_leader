"""Production-grade AI Engineering Operating System runtime.

This package turns a code repository into a governed engineering workspace:
context graph -> plan -> governance gate -> execution contract -> verification -> memory.
"""

from .models import (
    ContextGraph,
    EngineeringNode,
    EngineeringEdge,
    PhasePlan,
    GovernanceDecision,
    VerificationReport,
    SkillDefinition,
)
from .context_graph import build_context_graph
from .planner import create_phase_plan
from .governance import evaluate_phase_plan
from .verification import run_verification
from .memory import append_memory_event, load_memory_events
from .skills import load_skills, recommend_skills
from .runtime import run_engineering_os

__all__ = [
    "ContextGraph",
    "EngineeringNode",
    "EngineeringEdge",
    "PhasePlan",
    "GovernanceDecision",
    "VerificationReport",
    "SkillDefinition",
    "build_context_graph",
    "create_phase_plan",
    "evaluate_phase_plan",
    "run_verification",
    "append_memory_event",
    "load_memory_events",
    "load_skills",
    "recommend_skills",
    "run_engineering_os",
]
