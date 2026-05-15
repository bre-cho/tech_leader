from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .auto_fix import SafeAutoFixer
from .file_inventory import FileInventory
from .graph_builder import ContextGraphBuilder
from .models import AgentContract, AuditReport, Finding, ReleaseGate
from .business_operating import BusinessOperatingMind
from .patch_planner import PatchPlanner
from .runtime_validation import RuntimeValidator
from .static_scan import StaticSystemScanner

@dataclass(frozen=True)
class Agent16Config:
    runtime: bool = False
    apply_safe_fixes: bool = False
    timeout_seconds: int = 45
    strict_live_trading: bool = True
    business_operating_mind: bool = True

class TechnicalLeadAgent:
    """Production senior-engineer Technical Lead Agent for the trading MVP.

    This agent performs real repo inspection, static scan, graph construction,
    runtime validation, safe auto-fixes, patch planning, and release gate decision.
    """

    def __init__(self, repo_root: str | Path = '.', config: Agent16Config | None = None) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.config = config or Agent16Config()
        self.inventory = FileInventory(self.repo_root)
        self.contracts = self._contracts()

    def run(self) -> AuditReport:
        findings: list[Finding] = []
        fixed: list[Finding] = []

        findings.extend(self._phase1_inventory_runtime_graph_detection())
        findings.extend(StaticSystemScanner(self.repo_root).scan())

        graph = ContextGraphBuilder(self.repo_root).write(self.repo_root / 'context_graph')
        findings.extend(self._graph_findings(graph))

        runtime_results: dict[str, Any] = {}
        if self.config.runtime:
            runtime_results, runtime_findings = RuntimeValidator(self.repo_root, self.config.timeout_seconds).validate()
            findings.extend(runtime_findings)

        findings.extend(self._phase4_architecture_audit(graph))

        if self.config.apply_safe_fixes:
            fixed = SafeAutoFixer(self.repo_root).apply()
            # rescan package import errors after safe init creation is intentionally not performed here

        business_os = {}
        business_gate = None
        if self.config.business_operating_mind:
            business_report = BusinessOperatingMind(self.repo_root).run(findings, graph)
            business_report.write(self.repo_root / ".agent16-business-os")
            business_os = business_report.to_dict()
            business_gate = business_report.release_gate

        patch_plan = PatchPlanner().plan(findings)
        gate = self._merge_release_gates(self._release_gate(findings), business_gate)
        summary = self._summary(findings, fixed, gate, graph)
        return AuditReport(
            repo_root=str(self.repo_root),
            release_gate=gate,
            executive_summary=summary,
            findings=findings,
            graph=graph.get('summary', {}),
            runtime_results=runtime_results,
            patch_plan=patch_plan,
            fixed=fixed,
            direct_commands=self.direct_commands(),
            business_operating=business_os,
        )

    def _contracts(self) -> list[AgentContract]:
        return [
            AgentContract('Technical Lead Agent','Own audit, patch plan, release gate',['repo','policy'],['audit_report','patch_plan','release_gate'], live_trading_sensitive=True),
            AgentContract('Planning Agent','Build closed-loop trading plan before coding/execution',['goal','constraints'],['plan']),
            AgentContract('Market Data Agent','Fetch and validate independent OHLCV/Bid/Ask/Spread',['symbol','timeframe'],['market_snapshot','data_quality_report']),
            AgentContract('Grid Math Agent','Convert price to Step/X-level coordinates',['price','step_size','base_price'],['grid_coordinates']),
            AgentContract('Hedge Strategy Agent','Evaluate Buy/Sell hedge and surplus state',['positions','grid_coordinates'],['hedge_decision']),
            AgentContract('FSM Brain Agent','Control state transitions',['robot_state','events'],['next_state','action_plan']),
            AgentContract('Risk Guard Agent','Block unsafe execution',['equity','drawdown','spread','margin'],['allow_execution','guard_events'], live_trading_sensitive=True),
            AgentContract('Execution Agent','Submit idempotent broker orders only after guard approval',['approved_order_intent'],['execution_log','broker_order_id'],['Risk Guard Agent'], True),
            AgentContract('Sweep Agent','Detect and resolve orphan/stale/pending orders',['broker_state','db_state'],['sweep_report'], live_trading_sensitive=True),
            AgentContract('Backtest Optimization Agent','Search/reject/promote gene sets',['history','gene_space'],['best_gene_set','failed_gene_sets']),
            AgentContract('Dashboard Agent','Expose runtime truth',['runtime_snapshot'],['dashboard_state']),
            AgentContract('Memory Learning Agent','Persist verified outcomes and lessons',['trade_results','audit'],['memory_update']),
            AgentContract('Agent 16 — TrustGraph Code Audit Agent','Detect and safely patch code/graph/runtime/memory/release risks',['repo'],['audit_report','safe_fixes','release_gate'], live_trading_sensitive=True),
        ]

    def _phase1_inventory_runtime_graph_detection(self) -> list[Finding]:
        findings=[]
        required = {
            'monorepo topology': ['backend', 'frontend', 'ai_trading_brain', 'docker-compose.yml'],
            'Context Graph layer': ['context_graph', 'ai_trading_brain/techlead/graph_builder.py'],
            'TrustGraph orchestration': ['.ai-workforce', 'AGENTS.md', 'ai_trading_brain/techlead/agent16.py'],
            'agent runtime': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py'],
            'memory store': ['ai_trading_brain/memory_engine.py', 'memory'],
            'runtime governance': ['ai_trading_brain/governance.py'],
            'observability': ['reports', 'backend/main.py'],
        }
        for label, candidates in required.items():
            if not self.inventory.exists_any(candidates):
                findings.append(Finding('P1','PHASE_1_INVENTORY_RUNTIME_GRAPH_DETECTION','inventory', '.', f'Missing {label}.', f'Add at least one of: {candidates}', {'expected_any': candidates}))
        return findings

    def _graph_findings(self, graph: dict[str, Any]) -> list[Finding]:
        out=[]
        for s in graph.get('risk_signals', []):
            out.append(Finding(s.get('severity','P2'),'PHASE_1_INVENTORY_RUNTIME_GRAPH_DETECTION','context-graph', '.', f"Graph risk signal: {s.get('type')}", 'Review graph risk signal and patch the referenced layer.', s))
        if graph.get('summary', {}).get('entities', 0) == 0:
            out.append(Finding('P1','PHASE_1_INVENTORY_RUNTIME_GRAPH_DETECTION','context-graph', '.', 'Context graph produced zero entities.', 'Check repo path and file permissions.'))
        return out

    def _phase4_architecture_audit(self, graph: dict[str, Any]) -> list[Finding]:
        out=[]
        edges = graph.get('edges', [])
        edge_text = '\n'.join([str(e) for e in edges[:5000]])
        if 'governance' not in edge_text.lower():
            out.append(Finding('P2','PHASE_4_ARCHITECTURE_AUDIT','governance-drift','.', 'Graph does not show clear governance coupling.', 'Wire TradingBrainGovernance/RiskGuard into execution flow and tests.'))
        if 'memory' not in edge_text.lower():
            out.append(Finding('P2','PHASE_4_ARCHITECTURE_AUDIT','memory-consistency','.', 'Graph does not show clear memory coupling.', 'Ensure MemoryLearningAgent records verified outcomes only.'))
        if self.config.strict_live_trading:
            out.extend(self._live_trading_contract_audit())
        return out

    def _live_trading_contract_audit(self) -> list[Finding]:
        findings=[]
        names = [c.name for c in self.contracts]
        required = ['Risk Guard Agent','Execution Agent','Sweep Agent','Memory Learning Agent','Agent 16 — TrustGraph Code Audit Agent']
        for r in required:
            if r not in names:
                findings.append(Finding('P0','PHASE_4_ARCHITECTURE_AUDIT','workforce-contract','.',f'Missing workforce contract: {r}.', 'Define contract before live trading.'))
        return findings

    def _release_gate(self, findings: list[Finding]) -> ReleaseGate:
        if any(f.severity == 'P0' for f in findings):
            return ReleaseGate.NO_GO
        if any(f.severity == 'P1' for f in findings):
            return ReleaseGate.NO_GO
        if any(f.severity == 'P2' for f in findings):
            return ReleaseGate.REVIEW
        return ReleaseGate.GO

    def _merge_release_gates(self, base_gate: ReleaseGate, business_gate: ReleaseGate | None) -> ReleaseGate:
        if business_gate is None:
            return base_gate
        order = {ReleaseGate.GO: 0, ReleaseGate.REVIEW: 1, ReleaseGate.NO_GO: 2}
        return business_gate if order[business_gate] > order[base_gate] else base_gate

    def _summary(self, findings: list[Finding], fixed: list[Finding], gate: ReleaseGate, graph: dict[str, Any]) -> str:
        counts={k:0 for k in ['P0','P1','P2','P3','INFO']}
        for f in findings:
            counts[f.severity]=counts.get(f.severity,0)+1
        return (
            f"Agent 16 đã quét repo thật, dựng Context Graph ({graph.get('summary',{}).get('entities',0)} entities, "
            f"{graph.get('summary',{}).get('edges',0)} edges), phát hiện P0={counts['P0']}, P1={counts['P1']}, "
            f"P2={counts['P2']}, P3={counts['P3']}. Safe auto-fix applied={len(fixed)}. "
            f"Release gate hiện tại: {gate.value}. Với robot chạy tiền thật, chỉ được live khi gate=GO."
        )

    def direct_commands(self) -> dict[str, list[str]]:
        return {
            'Claude Code': [
                'python scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md',
                'python scripts/context_graph_builder.py . --out context_graph',
                'python -m compileall ai_trading_brain backend scripts',
                'python scripts/agent16_business_operating_mind.py . --out .agent16-business-os',
                'pytest -q',
                'Fix P0 first, then P1. Do not refactor unrelated architecture.',
            ],
            'Cursor': [
                'Open reports/agent16_audit_report.md',
                'Patch only Blocking Errors P0/P1 with file-by-file minimal changes.',
                'Run python scripts/agent16_audit.py . --runtime after each patch batch.',
            ],
            'Copilot': [
                'Use AGENTS.md as workspace policy.',
                'Generate tests for every patched production module.',
                'Never add broker live execution without Risk Guard preflight and idempotency.',
            ],
            'Local CI': [
                'mkdir -p reports context_graph',
                'python scripts/agent16_audit.py . --runtime --json-out reports/agent16_audit_report.json',
                'python -m compileall ai_trading_brain backend scripts',
                'python scripts/agent16_business_operating_mind.py . --out .agent16-business-os',
                'pytest -q',
            ],
        }
