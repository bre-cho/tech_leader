from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .budget_allocator import BudgetAllocationOptimizer, BudgetRecommendation
from .capital_efficiency import CapitalEfficiencyEngine, CapitalEfficiencyScore
from .cashflow_diagnosis import CashflowDiagnosis, CashflowDiagnosisEngine
from .finance_signal_engine import FinanceSignalEngine, FinanceSnapshot
from .financial_memory import FinancialMemoryEvent, FinancialMemoryStore
from .scenario_simulator import FinancialScenarioSimulator, ScenarioResult


@dataclass(frozen=True)
class FinanceOperatingReport:
    snapshot: FinanceSnapshot
    diagnoses: list[CashflowDiagnosis]
    capital_efficiency: CapitalEfficiencyScore
    budget_recommendations: list[BudgetRecommendation]
    scenarios: list[ScenarioResult]
    ai_ceo_decision: dict[str, Any]
    execution_plan: list[dict[str, Any]]
    memory_events: list[FinancialMemoryEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            'snapshot': self.snapshot.to_dict(),
            'diagnoses': [d.to_dict() for d in self.diagnoses],
            'capital_efficiency': self.capital_efficiency.to_dict(),
            'budget_recommendations': [b.to_dict() for b in self.budget_recommendations],
            'scenarios': [s.to_dict() for s in self.scenarios],
            'ai_ceo_decision': self.ai_ceo_decision,
            'execution_plan': self.execution_plan,
            'memory_events': [m.to_dict() for m in self.memory_events],
        }

    def write(self, out_dir: str | Path) -> None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / 'finance_operating_report.json').write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
        (out / 'finance_operating_report.md').write_text(self.to_markdown(), encoding='utf-8')

    def to_markdown(self) -> str:
        lines = [
            '# Finance Operating Report', '',
            f'Company: `{self.snapshot.company_id}`',
            f'Capital Efficiency: **{self.capital_efficiency.score} / 100** ({self.capital_efficiency.grade})',
            f'Decision: **{self.capital_efficiency.decision}**', '',
            '## Key Signals',
        ]
        for k, v in self.snapshot.signals.items():
            lines.append(f'- `{k}`: `{round(v, 4)}`')
        lines += ['', '## Diagnoses']
        for d in self.diagnoses:
            lines.append(f'- **{d.severity}** `{d.code}` — {d.message}')
        lines += ['', '## Budget Allocation']
        for b in self.budget_recommendations:
            lines.append(f'- `{b.channel}` → **{b.action}**: {b.current_budget} → {b.recommended_budget}. {b.reason}')
        lines += ['', '## Scenario Simulator']
        for s in self.scenarios:
            lines.append(f'- `{s.name}`: runway `{s.runway_months}`, risk `{s.cash_risk}`, action `{s.recommended_action}`')
        lines += ['', '## AI CEO Decision', '```json', json.dumps(self.ai_ceo_decision, ensure_ascii=False, indent=2), '```']
        return '\n'.join(lines) + '\n'


class FinanceOperatingRuntime:
    """End-to-end Finance Intelligence Layer for AI Business OS.

    Flow:
    finance rows/CSV -> signals -> diagnosis -> capital efficiency -> budget allocation
    -> scenario simulation -> AI CEO decision -> execution plan -> financial memory.
    """

    def __init__(self, memory_path: str | Path = '.finance-os/financial_memory.jsonl') -> None:
        self.signal_engine = FinanceSignalEngine()
        self.diagnosis_engine = CashflowDiagnosisEngine()
        self.capital_engine = CapitalEfficiencyEngine()
        self.allocator = BudgetAllocationOptimizer()
        self.simulator = FinancialScenarioSimulator()
        self.memory = FinancialMemoryStore(memory_path)

    def run_rows(self, rows: list[dict[str, Any]], company_id: str = 'default', cash_balance: float | None = None, next_budget: float | None = None) -> FinanceOperatingReport:
        snapshot = self.signal_engine.from_rows(rows, company_id=company_id, cash_balance=cash_balance)
        return self._run_snapshot(snapshot, next_budget=next_budget)

    def run_file(self, path: str | Path, company_id: str = 'default', next_budget: float | None = None) -> FinanceOperatingReport:
        p = Path(path)
        if p.suffix.lower() == '.json':
            snapshot = self.signal_engine.from_json(p, company_id=company_id)
        else:
            snapshot = self.signal_engine.from_csv(p, company_id=company_id)
        return self._run_snapshot(snapshot, next_budget=next_budget)

    def _run_snapshot(self, snapshot: FinanceSnapshot, next_budget: float | None = None) -> FinanceOperatingReport:
        diagnoses = self.diagnosis_engine.diagnose(snapshot)
        capital = self.capital_engine.score(snapshot, diagnoses)
        budget = self.allocator.allocate(snapshot, capital, next_budget=next_budget)
        scenarios = self.simulator.simulate(snapshot)
        decision = self._ai_ceo_decision(snapshot, diagnoses, capital, budget, scenarios)
        execution = self._execution_plan(decision, diagnoses, budget)
        memory_events = self.memory.build_events(snapshot, diagnoses, capital, budget)
        self.memory.append(memory_events)
        return FinanceOperatingReport(snapshot, diagnoses, capital, budget, scenarios, decision, execution, memory_events)

    def _ai_ceo_decision(
        self,
        snapshot: FinanceSnapshot,
        diagnoses: list[CashflowDiagnosis],
        capital: CapitalEfficiencyScore,
        budget: list[BudgetRecommendation],
        scenarios: list[ScenarioResult],
    ) -> dict[str, Any]:
        critical = [d for d in diagnoses if d.severity == 'critical']
        high = [d for d in diagnoses if d.severity == 'high']
        if critical:
            mode = 'cash_protection'
            authority = 'human_approval_required'
        elif capital.decision == 'SCALE_CONTROLLED':
            mode = 'controlled_growth'
            authority = 'auto_execute_with_budget_cap'
        elif high:
            mode = 'optimize_before_scale'
            authority = 'execute_with_review'
        else:
            mode = 'hold_and_learn'
            authority = 'execute_with_review'
        return {
            'mode': mode,
            'authority': authority,
            'capital_efficiency_score': capital.score,
            'primary_bottlenecks': [d.code for d in diagnoses if d.code != 'financial_state_stable'],
            'budget_actions': {b.channel: b.action for b in budget},
            'scenario_risks': {s.name: s.cash_risk for s in scenarios},
            'guardrails': [
                'No budget scale if runway < 3 months.',
                'No paid growth scale if LTV/CAC < 3 unless explicitly approved.',
                'Reduce channels with ROI < 1 when cash protection mode is active.',
                'Write finance memory only from measured or simulated evidence.',
            ],
            'recommended_focus': self._recommended_focus(capital, diagnoses),
            'signals': snapshot.signals,
        }

    def _recommended_focus(self, capital: CapitalEfficiencyScore, diagnoses: list[CashflowDiagnosis]) -> list[str]:
        codes = {d.code for d in diagnoses}
        focus: list[str] = []
        if 'runway_risk' in codes:
            focus += ['protect cash', 'cut non-essential spend', 'extend runway']
        if 'growth_efficiency_collapse' in codes:
            focus += ['repair LTV/CAC', 'improve retention', 'pause weak acquisition scale']
        if 'budget_leakage' in codes:
            focus += ['reallocate budget to high ROI channels', 'audit campaign attribution']
        if 'margin_compression' in codes:
            focus += ['pricing review', 'COGS reduction', 'bundle/upsell margin repair']
        if not focus:
            focus = ['controlled experiments', 'compound winner memory', 'monitor drift weekly']
        return focus

    def _execution_plan(self, decision: dict[str, Any], diagnoses: list[CashflowDiagnosis], budget: list[BudgetRecommendation]) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for idx, d in enumerate([x for x in diagnoses if x.code != 'financial_state_stable'], 1):
            steps.append({
                'id': f'FIN-DIAG-{idx:03d}',
                'stage': 'diagnosis_response',
                'owner_agent': self._agent_for_diagnosis(d.code),
                'action': d.recommended_actions[0] if d.recommended_actions else 'review',
                'acceptance_criteria': ['metric baseline captured', 'change owner assigned', 'next measurement date set'],
                'approval': 'required' if d.severity in {'critical', 'high'} else 'review',
            })
        for idx, b in enumerate(budget, 1):
            if b.action != 'hold':
                steps.append({
                    'id': f'FIN-BUDGET-{idx:03d}',
                    'stage': 'budget_allocation',
                    'owner_agent': 'finance-agent',
                    'action': f'{b.channel}: {b.action}',
                    'current_budget': b.current_budget,
                    'recommended_budget': b.recommended_budget,
                    'approval': 'required' if decision['authority'] == 'human_approval_required' else 'controlled',
                })
        if not steps:
            steps.append({'id': 'FIN-MONITOR-001', 'stage': 'monitoring', 'owner_agent': 'finance-agent', 'action': 'continue weekly finance signal monitoring', 'approval': 'none'})
        return steps

    def _agent_for_diagnosis(self, code: str) -> str:
        return {
            'runway_risk': 'finance-agent',
            'growth_efficiency_collapse': 'growth-efficiency-agent',
            'budget_leakage': 'budget-optimizer-agent',
            'margin_compression': 'offer-pricing-agent',
            'budget_variance_drift': 'governance-agent',
            'retention_ltv_risk': 'crm-retention-agent',
        }.get(code, 'finance-agent')
