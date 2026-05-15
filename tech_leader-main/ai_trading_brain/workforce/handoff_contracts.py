
from .agent_role_registry import DEFAULT_AGENT_ROLES

def build_handoff_contracts():
    roles=list(DEFAULT_AGENT_ROLES)
    return [{'from':roles[i],'to':roles[i+1],'payload':DEFAULT_AGENT_ROLES[roles[i]]['outputs']} for i in range(len(roles)-1)]
