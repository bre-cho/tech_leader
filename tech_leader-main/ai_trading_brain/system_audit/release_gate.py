
class ReleaseGate:
    def decide(self, report):
        blockers=[]
        if report.get('runtime',{}).get('status')=='FAIL': blockers.append('Runtime validation failed')
        if report.get('static',{}).get('status')=='FAIL': blockers.append('Static scan failed')
        if report.get('trustgraph',{}).get('trustgraph_status')=='FAIL': blockers.append('TrustGraph policy failure')
        if report.get('artifact_lineage',{}).get('artifact_lineage_status')=='FAIL': blockers.append('Artifact lineage failure')
        return {'release_status':'NO-GO' if blockers else 'GO','blockers':blockers,'conditions':['No P0 blockers','CI/tests pass','Context Graph loadable','TrustGraph has no critical violation','Artifact lineage minimum contract present','Replay/recovery manifest available when needed']}

def decide_release(report): return ReleaseGate().decide(report)
