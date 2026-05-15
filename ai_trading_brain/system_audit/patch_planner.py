
class PatchPlanner:
    def plan(self, report):
        items=[]
        if report.get('runtime',{}).get('status')=='FAIL': items.append({'priority':'P0','title':'Fix runtime blockers','files':['ai_trading_brain/**','scripts/**','tests/**']})
        if report.get('static',{}).get('status')!='PASS': items.append({'priority':'P1','title':'Fix static scan findings','files':['reported files']})
        if report.get('context_graph',{}).get('context_graph_status')!='PASS': items.append({'priority':'P2','title':'Repair Context Graph integrity','files':['ai_trading_brain/graphs/context_graph_integrity.py','docs/runtime/context-graph.json']})
        if report.get('trustgraph',{}).get('trustgraph_status')!='PASS': items.append({'priority':'P2','title':'Harden TrustGraph permissions','files':['ai_trading_brain/graphs/trustgraph_orchestrator.py']})
        if report.get('economic_flow',{}).get('economic_cognition_status')!='PASS': items.append({'priority':'P3','title':'Expand economic cognition flow','files':['ai_trading_brain/strategic_cognition/**']})
        return {'phase':'PHASE 5 — Patch Planning','patch_plan':items,'status':'READY' if items else 'NO_PATCH_NEEDED'}

def build_patch_plan(report): return PatchPlanner().plan(report)
