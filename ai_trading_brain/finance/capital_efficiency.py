from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .cashflow_diagnosis import CashflowDiagnosis
from .finance_signal_engine import FinanceSnapshot


@dataclass(frozen=True)
class CapitalEfficiencyScore:
    score: float
    grade: str
    revenue_growth_component: float
    burn_component: float
    margin_component: float
    unit_economics_component: float
    risk_penalty: float
    decision: str
    reasoning: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapitalEfficiencyEngine:
    """Scores whether capital should be scaled, held, or protected."""

    def score(self, snapshot: FinanceSnapshot, diagnoses: list[CashflowDiagnosis]) -> CapitalEfficiencyScore:
        s = snapshot.signals
        growth = _clamp((s['revenue_growth_rate'] + 0.5) / 1.5, 0, 1) * 30
        burn = _clamp(s['runway_months'] / 12, 0, 1) * 25
        margin = _clamp(s['gross_margin'] / 0.7, 0, 1) * 20
        unit = _clamp(s['ltv_cac_ratio'] / 4, 0, 1) * 25 if s['ltv_cac_ratio'] > 0 else 12
        penalty = 0.0
        reason: list[str] = []
        for d in diagnoses:
            if d.severity == 'critical':
                penalty += 22
            elif d.severity == 'high':
                penalty += 14
            elif d.severity == 'medium':
                penalty += 7
            if d.code != 'financial_state_stable':
                reason.append(f'{d.code}: {d.message}')
        final = _clamp(growth + burn + margin + unit - penalty, 0, 100)
        if final >= 78 and not any(d.severity in {'critical', 'high'} for d in diagnoses):
            decision = 'SCALE_CONTROLLED'
            grade = 'A'
        elif final >= 58:
            decision = 'HOLD_AND_OPTIMIZE'
            grade = 'B'
        elif final >= 38:
            decision = 'PROTECT_CASH_FIX_BOTTLENECKS'
            grade = 'C'
        else:
            decision = 'STOP_SCALE_RESTRUCTURE_FINANCE'
            grade = 'D'
        if not reason:
            reason.append('Finance signals are inside acceptable range; controlled experiments are allowed.')
        return CapitalEfficiencyScore(round(final, 2), grade, round(growth, 2), round(burn, 2), round(margin, 2), round(unit, 2), round(penalty, 2), decision, reason)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))
