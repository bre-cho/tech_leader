from app.creative_infra_mvp.contracts import OperatingStage

REQUIRED = [
    OperatingStage.target_define,
    OperatingStage.research,
    OperatingStage.plan,
    OperatingStage.execute,
    OperatingStage.verify,
    OperatingStage.distill_to_skill,
    OperatingStage.memory_update,
    OperatingStage.winner_dna_update,
]

class OperatingLawError(Exception):
    pass

class OperatingLaw:
    def validate(self, stages):
        missing = [s for s in REQUIRED if s not in stages]
        if missing:
            raise OperatingLawError("NO WORKFLOW → NO BUILD. Missing: " + ", ".join([m.value for m in missing]))
        return True
