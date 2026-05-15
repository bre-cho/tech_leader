
def default_escalation_policy():
    return {'P0':'human_approval_required','P1':'governance_review','P2':'auto_patch_with_review','P3':'backlog'}
