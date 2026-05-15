
from ai_trading_brain.system_audit.common import *
DEFAULT_AGENT_ROLES={
 'planner':{'inputs':['user_request','context_graph'],'outputs':['execution_plan']},
 'executor':{'inputs':['execution_plan'],'outputs':['artifact','execution_log']},
 'verifier':{'inputs':['artifact','execution_log'],'outputs':['verification_report']},
 'governance':{'inputs':['verification_report','risk_score'],'outputs':['release_decision']},
 'memory':{'inputs':['release_decision','artifact'],'outputs':['memory_record']}}
class AgentRoleRegistry:
    def roles(self): return DEFAULT_AGENT_ROLES

def get_default_agent_roles(): return DEFAULT_AGENT_ROLES
