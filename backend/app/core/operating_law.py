from __future__ import annotations

from app.core.contracts import WorkflowStage


REQUIRED_STAGES = [
    WorkflowStage.target_define,
    WorkflowStage.research,
    WorkflowStage.plan,
    WorkflowStage.execute,
    WorkflowStage.verify,
    WorkflowStage.distill_to_skill,
    WorkflowStage.memory_update,
    WorkflowStage.winner_dna_update,
]


class OperatingLawViolation(Exception):
    pass


class CoreOperatingLaw:
    '''
    Hardcoded non-bypassable law:
    NO WORKFLOW -> NO BUILD
    NO VERIFY -> NO PROMOTION
    NO MEMORY -> NO SCALE
    NO WINNER DNA -> NO OPTIMIZATION
    '''

    def validate_stages(self, completed):
        missing = [stage for stage in REQUIRED_STAGES if stage not in completed]
        if missing:
            raise OperatingLawViolation(
                "Blocked by Core Operating Law. Missing stages: "
                + ", ".join([m.value for m in missing])
            )
        return True

    def validate_feature_contract(self, contract):
        required = [
            "workflow",
            "agent",
            "skill",
            "runtime",
            "verification",
            "memory",
            "winner_dna",
        ]
        missing = [key for key in required if not contract.get(key)]
        if missing:
            raise OperatingLawViolation(
                "Feature rejected. Missing required contracts: " + ", ".join(missing)
            )
        return True
