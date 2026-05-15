from __future__ import annotations

"""Agent16 Business Operating Mind runtime.

This module adapts the AI Business OS production patch concepts to the
Agent16 technical-lead runtime.  It is intentionally dependency-light so it
can run in CI and on incomplete MVP repos.

It turns engineering signals into a governed economic cognition loop:

Economic/engineering signals -> business state -> causal graph -> AI CEO plan
-> workforce delegation -> execution runtime -> feedback intelligence ->
economic memory events -> release/promotion gate.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import math
import os

from .models import Finding, ReleaseGate

CODE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs', '.java'}
RUNTIME_HINTS = ('runtime', 'worker', 'execution', 'broker', 'order', 'api', 'service', 'task')
TEST_HINTS = ('test_', '.test.', '.spec.', '/tests/', '\\tests\\')
IGNORE_DIRS = {'.git', 'node_modules', '.next', 'dist', 'build', '.venv', 'venv', '__pycache__'}


@dataclass(frozen=True)
class BusinessSignal:
    name: str
    value: float
    severity: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ''


@dataclass(frozen=True)
class BusinessState:
    name: str
    severity: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    recommended_action: str = ''


@dataclass(frozen=True)
class CausalEdge:
    cause: str
    effect: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Opportunity:
    id: str
    title: str
    expected_impact: float
    confidence: float
    execution_cost: float
    risk_penalty: float
    economic_score: float
    reason: str


@dataclass(frozen=True)
class ResourceAllocation:
    domain: str
    allocation_percent: float
    reason: str


@dataclass(frozen=True)
class WorkforceWorkItem:
    id: str
    agent: str
    priority: str
    title: str
    execution_contract: dict[str, Any]
    acceptance_criteria: list[str]
    blocks_without: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExecutionStep:
    id: str
    stage: str
    capability: str
    provider: str
    validation_gate: str
    promotion_gate: str
    publishes: bool = False


@dataclass(frozen=True)
class FeedbackInsight:
    type: str
    severity: str
    message: str
    metric: str
    before: float | None = None
    after: float | None = None
    recommendation: str = ''


@dataclass(frozen=True)
class MemoryEvent:
    event_type: str
    key: str
    weight: float
    decay_days: int
    context: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class BusinessOperatingReport:
    generated_at: str
    repo_root: str
    signals: list[BusinessSignal]
    states: list[BusinessState]
    causal_edges: list[CausalEdge]
    opportunities: list[Opportunity]
    resource_allocation: list[ResourceAllocation]
    workforce_plan: list[WorkforceWorkItem]
    execution_plan: list[ExecutionStep]
    feedback_insights: list[FeedbackInsight]
    trust_graph: dict[str, dict[str, Any]]
    memory_events: list[MemoryEvent]
    adaptive_deployment: dict[str, Any]
    release_gate: ReleaseGate
    context_graph: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data['release_gate'] = self.release_gate.value
        return data

    def write(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'business_operating_report.json').write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8'
        )
        (out_dir / 'business_operating_report.md').write_text(self.to_markdown(), encoding='utf-8')
        graph_dir = out_dir / 'business_context_graph'
        graph_dir.mkdir(parents=True, exist_ok=True)
        _write_jsonl(graph_dir / 'entities.jsonl', self.context_graph.get('entities', []))
        _write_jsonl(graph_dir / 'edges.jsonl', self.context_graph.get('edges', []))
        with (out_dir / 'economic_memory_events.jsonl').open('a', encoding='utf-8') as f:
            for event in self.memory_events:
                f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')

    def to_markdown(self) -> str:
        lines = [
            '# Agent16 Business Operating Mind Report',
            '',
            f'Generated: `{self.generated_at}`',
            f'Repo: `{self.repo_root}`',
            f'Release Gate: **{self.release_gate.value}**',
            '',
            '## Business States',
        ]
        for s in self.states:
            lines.append(f'- **{s.severity}** `{s.name}` — confidence `{s.confidence}`; {s.recommended_action}')
        lines += ['', '## Opportunity Ranking']
        for o in self.opportunities[:10]:
            lines.append(f'- **{o.title}** — score `{o.economic_score}`; impact `{o.expected_impact}`; reason: {o.reason}')
        lines += ['', '## Workforce Delegation']
        for w in self.workforce_plan:
            lines.append(f'- `{w.priority}` `{w.agent}` — {w.title}')
        lines += ['', '## Execution Runtime Plan']
        for e in self.execution_plan:
            lines.append(f'- `{e.stage}` `{e.capability}` via `{e.provider}` → gate `{e.promotion_gate}`')
        lines += ['', '## Feedback / Drift Insights']
        for i in self.feedback_insights:
            lines.append(f'- **{i.severity}** `{i.type}` — {i.message}')
        lines += ['', '## Adaptive Deployment Decision', '```json', json.dumps(self.adaptive_deployment, ensure_ascii=False, indent=2), '```']
        return '\n'.join(lines) + '\n'


class BusinessOperatingMind:
    """Production-grade cognition layer for Agent16.

    It does not call brokers or external APIs.  It creates an actionable,
    auditable plan that can govern real execution modules.
    """

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()

    def run(self, findings: list[Finding], base_graph: dict[str, Any] | None = None) -> BusinessOperatingReport:
        files = self._walk_files()
        signals = self._derive_signals(files, findings, base_graph or {})
        states, causal_edges = self._derive_business_state(signals, findings)
        opportunities = self._rank_opportunities(signals, states)
        allocation = self._allocate_resources(opportunities, states)
        workforce = self._delegate_work(opportunities, states)
        execution_plan = self._build_execution_plan(workforce, states)
        feedback = self._feedback_intelligence(signals, states)
        trust = self._trust_graph(workforce, findings, states)
        memory = self._memory_events(opportunities, states, trust, feedback)
        adaptive = self._adaptive_deployment_decision(opportunities, states, trust, feedback)
        gate = self._release_gate(findings, states, adaptive)
        graph = self._context_graph(files, states, causal_edges, opportunities, workforce, execution_plan, base_graph or {})
        return BusinessOperatingReport(
            generated_at=_now_iso(),
            repo_root=str(self.repo_root),
            signals=signals,
            states=states,
            causal_edges=causal_edges,
            opportunities=opportunities,
            resource_allocation=allocation,
            workforce_plan=workforce,
            execution_plan=execution_plan,
            feedback_insights=feedback,
            trust_graph=trust,
            memory_events=memory,
            adaptive_deployment=adaptive,
            release_gate=gate,
            context_graph=graph,
        )

    def _walk_files(self) -> list[Path]:
        files: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(self.repo_root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for name in filenames:
                files.append(Path(dirpath) / name)
        return files

    def _derive_signals(self, files: list[Path], findings: list[Finding], graph: dict[str, Any]) -> list[BusinessSignal]:
        code_files = [p for p in files if p.suffix in CODE_EXTENSIONS]
        tests = [p for p in files if any(h in _rel(self.repo_root, p).lower() for h in TEST_HINTS)]
        runtime_files = [p for p in code_files if any(h in _rel(self.repo_root, p).lower() for h in RUNTIME_HINTS)]
        docs = [p for p in files if p.suffix.lower() in {'.md', '.mdx'}]
        migrations = [p for p in files if 'migration' in _rel(self.repo_root, p).lower() or 'alembic/versions' in _rel(self.repo_root, p).lower()]
        p0 = sum(1 for f in findings if f.severity == 'P0')
        p1 = sum(1 for f in findings if f.severity == 'P1')
        p2 = sum(1 for f in findings if f.severity == 'P2')
        test_ratio = len(tests) / max(1, len(code_files))
        runtime_risk = sum(1 for f in findings if any(h in f.path.lower() for h in RUNTIME_HINTS))
        graph_entities = float(graph.get('summary', {}).get('entities', 0) if isinstance(graph.get('summary'), dict) else 0)
        return [
            BusinessSignal('p0_blockers', float(p0), 'critical' if p0 else 'ok', [f.path for f in findings if f.severity == 'P0'][:10], 'Fix before any release.'),
            BusinessSignal('p1_high_risk', float(p1), 'high' if p1 else 'ok', [f.path for f in findings if f.severity == 'P1'][:10], 'Require owner approval and mitigation.'),
            BusinessSignal('p2_runtime_debt', float(p2), 'medium' if p2 > 10 else 'ok', [f.path for f in findings if f.severity == 'P2'][:10], 'Prioritize runtime paths first.'),
            BusinessSignal('test_coverage_proxy', round(test_ratio, 4), 'high' if test_ratio < 0.08 else 'ok', [_rel(self.repo_root, p) for p in tests[:10]], 'Add tests around changed modules.'),
            BusinessSignal('runtime_surface_area', float(len(runtime_files)), 'info', [_rel(self.repo_root, p) for p in runtime_files[:10]], 'Use stronger gates for larger runtime surface.'),
            BusinessSignal('runtime_risk_density', round(runtime_risk / max(1, len(runtime_files)), 4), 'high' if runtime_files and runtime_risk / max(1, len(runtime_files)) > 0.25 else 'ok', [f.path for f in findings if any(h in f.path.lower() for h in RUNTIME_HINTS)][:10], 'Reduce runtime risk density.'),
            BusinessSignal('migration_count', float(len(migrations)), 'info', [_rel(self.repo_root, p) for p in migrations[:10]], 'Run DB migration validation when present.'),
            BusinessSignal('docs_count', float(len(docs)), 'info', [], 'Keep docs synced to code decisions.'),
            BusinessSignal('context_graph_entities', graph_entities, 'high' if graph_entities == 0 else 'ok', [], 'Regenerate context graph if empty.'),
        ]

    def _derive_business_state(self, signals: list[BusinessSignal], findings: list[Finding]) -> tuple[list[BusinessState], list[CausalEdge]]:
        sv = {s.name: s.value for s in signals}
        states: list[BusinessState] = []
        edges: list[CausalEdge] = []
        if sv.get('p0_blockers', 0) > 0:
            states.append(BusinessState('release_blocked_by_correctness_risk', 'critical', 0.99, [f.path for f in findings if f.severity == 'P0'][:8], 'Patch P0 before any execution or publish.'))
            edges.append(CausalEdge('syntax_or_runtime_failure', 'release_blocked', 0.98, [f.path for f in findings if f.severity == 'P0'][:5]))
        if sv.get('p1_high_risk', 0) > 0:
            states.append(BusinessState('governance_risk_requires_approval', 'high', 0.91, [f.path for f in findings if f.severity == 'P1'][:8], 'Route through release-gate-agent and human approval.'))
            edges.append(CausalEdge('high_risk_change', 'human_approval_required', 0.9, [f.path for f in findings if f.severity == 'P1'][:5]))
        if sv.get('test_coverage_proxy', 1) < 0.08:
            states.append(BusinessState('low_verification_coverage', 'high', 0.84, ['test_coverage_proxy < 0.08'], 'Add deterministic tests and smoke checks around runtime flows.'))
            edges.append(CausalEdge('low_test_coverage', 'higher_regression_probability', 0.82, ['test_coverage_proxy < 0.08']))
        if sv.get('runtime_risk_density', 0) > 0.25:
            states.append(BusinessState('runtime_surface_has_concentrated_risk', 'high', 0.8, ['runtime_risk_density > 0.25'], 'Stabilize runtime services before adding new features.'))
            edges.append(CausalEdge('runtime_debt', 'production_failure_probability', 0.78, ['runtime_risk_density > 0.25']))
        if sv.get('context_graph_entities', 1) == 0:
            states.append(BusinessState('context_graph_memory_gap', 'medium', 0.75, ['context_graph_entities == 0'], 'Regenerate graph and persist decision evidence.'))
            edges.append(CausalEdge('missing_graph_evidence', 'weak_decision_traceability', 0.76, ['empty context graph']))
        if not states:
            states.append(BusinessState('release_review_ready', 'ok', 0.7, [], 'Proceed through standard release gate with evidence.'))
        return states, edges

    def _rank_opportunities(self, signals: list[BusinessSignal], states: list[BusinessState]) -> list[Opportunity]:
        sv = {s.name: s.value for s in signals}
        state_names = {s.name for s in states}
        candidates = [
            ('fix_p0_correctness', 'Fix P0 correctness blockers', 100 if sv.get('p0_blockers', 0) else 0, 0.98, 28, 10, 'P0 blocks all downstream execution.'),
            ('govern_release_risk', 'Harden governance and approval chain', 82 if sv.get('p1_high_risk', 0) else 35, 0.86, 24, 8, 'P1 risk requires weighted governance.'),
            ('add_verification_layer', 'Add release verification tests and smoke checks', 78 if 'low_verification_coverage' in state_names else 38, 0.82, 30, 9, 'Verification coverage is the cheapest way to reduce regression risk.'),
            ('reduce_runtime_debt', 'Patch runtime debt in execution/API/worker paths', min(92, 45 + sv.get('runtime_risk_density', 0) * 160), 0.78, 42, 14, 'Runtime risk has high blast radius.'),
            ('sync_context_graph', 'Regenerate Context Graph and attach evidence to decisions', 66 if 'context_graph_memory_gap' in state_names else 42, 0.76, 18, 5, 'Decision traceability improves AI workforce coordination.'),
            ('build_feedback_memory', 'Persist feedback intelligence and economic memory events', 62, 0.74, 22, 6, 'Memory evolution compounds future audit quality.'),
            ('adaptive_deployment_gate', 'Add adaptive deployment decision gate', 68, 0.7, 26, 7, 'Prevents auto-deploy when trust or evidence is weak.'),
        ]
        out: list[Opportunity] = []
        for cid, title, impact, confidence, cost, risk, reason in candidates:
            if impact <= 0:
                continue
            score = (impact * confidence) - (cost * 0.35) - risk
            out.append(Opportunity(cid, title, round(float(impact), 2), confidence, float(cost), float(risk), round(score, 2), reason))
        return sorted(out, key=lambda x: x.economic_score, reverse=True)

    def _allocate_resources(self, opportunities: list[Opportunity], states: list[BusinessState]) -> list[ResourceAllocation]:
        if not opportunities:
            return [ResourceAllocation('standard_maintenance', 100.0, 'No ranked opportunities found.')]
        buckets = {'correctness': 0.0, 'governance': 0.0, 'verification': 0.0, 'runtime': 0.0, 'memory_graph': 0.0}
        for opp in opportunities[:5]:
            if 'p0' in opp.id or 'correctness' in opp.id:
                buckets['correctness'] += opp.economic_score
            elif 'govern' in opp.id or 'deployment' in opp.id:
                buckets['governance'] += opp.economic_score
            elif 'verification' in opp.id:
                buckets['verification'] += opp.economic_score
            elif 'runtime' in opp.id:
                buckets['runtime'] += opp.economic_score
            else:
                buckets['memory_graph'] += opp.economic_score
        total = sum(max(0, v) for v in buckets.values()) or 1.0
        return [ResourceAllocation(k, round(max(0, v) / total * 100, 2), f'Allocated from opportunity scores and states: {[s.name for s in states]}') for k, v in buckets.items() if v > 0]

    def _delegate_work(self, opportunities: list[Opportunity], states: list[BusinessState]) -> list[WorkforceWorkItem]:
        agent_map = {
            'fix_p0_correctness': 'code-review-agent',
            'govern_release_risk': 'release-gate-agent',
            'add_verification_layer': 'tdd-agent',
            'reduce_runtime_debt': 'runtime-hardening-agent',
            'sync_context_graph': 'context-graph-agent',
            'build_feedback_memory': 'memory-learning-agent',
            'adaptive_deployment_gate': 'optimization-agent',
        }
        state_names = {s.name for s in states}
        items: list[WorkforceWorkItem] = []
        for idx, opp in enumerate(opportunities[:8], 1):
            priority = 'P0' if opp.expected_impact >= 95 or 'release_blocked_by_correctness_risk' in state_names and idx == 1 else 'P1' if opp.economic_score >= 35 else 'P2'
            agent = agent_map.get(opp.id, 'strategic-cognition-agent')
            contract = {
                'required_inputs': ['audit_report', 'context_graph', 'release_policy'],
                'produced_outputs': ['patch_plan', 'verification_evidence', 'gate_decision'],
                'budget_policy': 'recommend_only_until_release_gate_passes' if priority in {'P0', 'P1'} else 'execute_with_review',
                'rollback_required': True,
            }
            items.append(WorkforceWorkItem(
                id=f'BOS-{idx:03d}',
                agent=agent,
                priority=priority,
                title=opp.title,
                execution_contract=contract,
                acceptance_criteria=[
                    'Changed files are listed file-by-file.',
                    'A deterministic verification command exists.',
                    'Context graph evidence is updated.',
                    'Release gate is PASS or explicit REVIEW with owner.',
                ],
                blocks_without=['release-gate-agent'] if priority in {'P0', 'P1'} else [],
            ))
        return items

    def _build_execution_plan(self, work_items: list[WorkforceWorkItem], states: list[BusinessState]) -> list[ExecutionStep]:
        steps: list[ExecutionStep] = []
        for idx, item in enumerate(work_items, 1):
            capability = item.agent.replace('-agent', '')
            provider = 'local_python_runtime' if capability in {'code-review', 'tdd', 'context-graph', 'runtime-hardening'} else 'governed_ai_workforce'
            steps.append(ExecutionStep(
                id=f'EXEC-{idx:03d}',
                stage='plan' if idx == 1 else 'execute',
                capability=capability,
                provider=provider,
                validation_gate='py_compile + pytest/smoke + context_graph_delta',
                promotion_gate='NO_AUTO_PUBLISH_IF_P0_OR_LOW_TRUST',
                publishes=False,
            ))
        steps.append(ExecutionStep('EXEC-PROMOTE', 'promotion', 'release-gate', 'agent16_release_gate', 'audit_report_json', 'GO_REQUIRED', False))
        return steps

    def _feedback_intelligence(self, signals: list[BusinessSignal], states: list[BusinessState]) -> list[FeedbackInsight]:
        sv = {s.name: s.value for s in signals}
        insights: list[FeedbackInsight] = []
        if sv.get('p2_runtime_debt', 0) > 10:
            insights.append(FeedbackInsight('drift_detection', 'medium', 'Runtime quality debt is accumulating.', 'p2_runtime_debt', recommendation='Schedule debt burn-down before expanding features.'))
        if sv.get('test_coverage_proxy', 1) < 0.08:
            insights.append(FeedbackInsight('verification_drift', 'high', 'Verification coverage proxy is below production threshold.', 'test_coverage_proxy', after=sv.get('test_coverage_proxy'), recommendation='Add tests before promotion.'))
        if sv.get('runtime_risk_density', 0) > 0.25:
            insights.append(FeedbackInsight('runtime_risk_concentration', 'high', 'Risk is concentrated in runtime files.', 'runtime_risk_density', after=sv.get('runtime_risk_density'), recommendation='Patch runtime paths first.'))
        if not insights:
            insights.append(FeedbackInsight('standard_feedback_loop', 'ok', 'No major drift detected; keep memory and graph updated.', 'overall', recommendation='Continue standard audit cadence.'))
        return insights

    def _trust_graph(self, work_items: list[WorkforceWorkItem], findings: list[Finding], states: list[BusinessState]) -> dict[str, dict[str, Any]]:
        p0 = sum(1 for f in findings if f.severity == 'P0')
        p1 = sum(1 for f in findings if f.severity == 'P1')
        agents = sorted({w.agent for w in work_items} | {'strategic-cognition-agent', 'governance-agent', 'memory-learning-agent'})
        trust: dict[str, dict[str, Any]] = {}
        for agent in agents:
            score = 0.84
            if agent in {'release-gate-agent', 'governance-agent'} and p1:
                score += 0.05
            if agent in {'code-review-agent', 'runtime-hardening-agent'} and p0:
                score += 0.06
            if p0 and agent not in {'code-review-agent', 'runtime-hardening-agent', 'release-gate-agent'}:
                score -= 0.12
            score = max(0.35, min(0.98, score))
            trust[agent] = {
                'trust_score': round(score, 3),
                'authority': 'auto_execute' if score >= 0.9 and not p0 else 'execute_with_review' if not p0 else 'recommend_only',
                'risk_notes': ['P0 present: no autonomous publish'] if p0 else [],
            }
        return trust

    def _memory_events(self, opportunities: list[Opportunity], states: list[BusinessState], trust: dict[str, dict[str, Any]], feedback: list[FeedbackInsight]) -> list[MemoryEvent]:
        top = opportunities[0] if opportunities else None
        return [
            MemoryEvent(
                event_type='operating_state_snapshot',
                key=_hash('|'.join(s.name for s in states)),
                weight=0.85 if any(s.severity in {'critical', 'high'} for s in states) else 0.55,
                decay_days=30,
                context={'states': [asdict(s) for s in states], 'top_opportunity': asdict(top) if top else None},
                created_at=_now_iso(),
            ),
            MemoryEvent(
                event_type='trust_graph_snapshot',
                key=_hash(json.dumps(trust, sort_keys=True)),
                weight=0.7,
                decay_days=45,
                context={'trust_graph': trust, 'feedback': [asdict(f) for f in feedback]},
                created_at=_now_iso(),
            ),
        ]

    def _adaptive_deployment_decision(self, opportunities: list[Opportunity], states: list[BusinessState], trust: dict[str, dict[str, Any]], feedback: list[FeedbackInsight]) -> dict[str, Any]:
        state_names = {s.name for s in states}
        min_trust = min((v['trust_score'] for v in trust.values()), default=0.0)
        high_feedback = any(i.severity == 'high' for i in feedback)
        if 'release_blocked_by_correctness_risk' in state_names:
            decision = 'BLOCK_DEPLOYMENT'
        elif high_feedback or min_trust < 0.72:
            decision = 'REVIEW_BEFORE_DEPLOYMENT'
        else:
            decision = 'ALLOW_CONTROLLED_PROMOTION'
        return {
            'decision': decision,
            'min_agent_trust': round(float(min_trust), 3),
            'top_opportunity': asdict(opportunities[0]) if opportunities else None,
            'guardrails': [
                'No auto-publish when P0 exists.',
                'P1 requires explicit release-gate owner.',
                'Every patch requires deterministic verification evidence.',
                'Memory updates must be based on verified outcomes only.',
            ],
        }

    def _release_gate(self, findings: list[Finding], states: list[BusinessState], adaptive: dict[str, Any]) -> ReleaseGate:
        if any(f.severity in {'P0', 'P1'} for f in findings):
            return ReleaseGate.NO_GO
        if adaptive.get('decision') == 'REVIEW_BEFORE_DEPLOYMENT' or any(s.severity == 'high' for s in states):
            return ReleaseGate.REVIEW
        return ReleaseGate.GO

    def _context_graph(self, files: list[Path], states: list[BusinessState], causal_edges: list[CausalEdge], opportunities: list[Opportunity], work_items: list[WorkforceWorkItem], execution_plan: list[ExecutionStep], base_graph: dict[str, Any]) -> dict[str, Any]:
        entities: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        repo_id = 'repo:root'
        entities.append({'id': repo_id, 'type': 'Repo', 'name': self.repo_root.name, 'path': str(self.repo_root), 'evidence': 'business_os_scan'})
        for p in files[:2000]:
            rp = _rel(self.repo_root, p)
            if p.suffix in CODE_EXTENSIONS or p.suffix.lower() in {'.md', '.json', '.yml', '.yaml'}:
                fid = 'file:' + _hash(rp)
                entities.append({'id': fid, 'type': 'File', 'name': p.name, 'path': rp})
                edges.append({'source': repo_id, 'relation': 'CONTAINS', 'target': fid, 'evidence': rp})
        for s in states:
            sid = 'state:' + _hash(s.name)
            entities.append({'id': sid, 'type': 'BusinessState', 'name': s.name, 'severity': s.severity, 'confidence': s.confidence, 'evidence': s.evidence})
            edges.append({'source': repo_id, 'relation': 'HAS_STATE', 'target': sid, 'evidence': s.recommended_action})
        for c in causal_edges:
            cid = 'causal:' + _hash(c.cause + c.effect)
            entities.append({'id': cid, 'type': 'CausalEdge', 'name': f'{c.cause}->{c.effect}', 'confidence': c.confidence, 'evidence': c.evidence})
            edges.append({'source': 'state:' + _hash(c.cause), 'relation': 'CAUSES', 'target': 'state:' + _hash(c.effect), 'evidence': ','.join(c.evidence)})
        for o in opportunities:
            oid = 'opportunity:' + o.id
            entities.append({'id': oid, 'type': 'Opportunity', 'name': o.title, 'economic_score': o.economic_score, 'evidence': o.reason})
            edges.append({'source': repo_id, 'relation': 'HAS_OPPORTUNITY', 'target': oid, 'evidence': o.reason})
        for w in work_items:
            wid = 'work:' + w.id
            aid = 'agent:' + w.agent
            entities.append({'id': wid, 'type': 'WorkItem', 'name': w.title, 'priority': w.priority})
            entities.append({'id': aid, 'type': 'Agent', 'name': w.agent})
            edges.append({'source': wid, 'relation': 'ASSIGNED_TO', 'target': aid, 'evidence': json.dumps(w.execution_contract, ensure_ascii=False)})
        for e in execution_plan:
            eid = 'execution:' + e.id
            entities.append({'id': eid, 'type': 'ExecutionStep', 'name': e.capability, 'stage': e.stage, 'provider': e.provider})
            edges.append({'source': repo_id, 'relation': 'EXECUTES', 'target': eid, 'evidence': e.validation_gate})
        summary = {'entities': len(entities), 'edges': len(edges), 'base_graph_summary': base_graph.get('summary', {})}
        return {'summary': summary, 'entities': entities, 'edges': edges}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace('\\', '/')
    except Exception:
        return str(path).replace('\\', '/')


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8', errors='ignore')).hexdigest()[:16]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
