from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .capital_efficiency import CapitalEfficiencyEngine
from .cashflow_diagnosis import CashflowDiagnosisEngine
from .finance_signal_engine import FinancePeriod, FinanceSnapshot, FinanceSignalEngine


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    runway_months: float
    cash_risk: str
    growth_upside: float
    capital_efficiency: float
    recommended_action: str
    projected: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FinancialScenarioSimulator:
    """Runs deterministic what-if scenarios against the latest finance state."""

    def simulate(self, snapshot: FinanceSnapshot, scenarios: list[dict[str, Any]] | None = None) -> list[ScenarioResult]:
        if scenarios is None:
            scenarios = [
                {'name': 'increase_ads_30_percent', 'ad_spend_delta': 0.30, 'revenue_delta': 0.12},
                {'name': 'cac_increase_20_percent', 'cac_delta': 0.20},
                {'name': 'revenue_down_15_percent', 'revenue_delta': -0.15, 'cash_in_delta': -0.15},
                {'name': 'retention_up_10_percent', 'retention_delta': 0.10, 'ltv_delta': 0.10},
                {'name': 'burn_rate_flat_6_months', 'months': 6},
            ]
        return [self._one(snapshot, sc) for sc in scenarios]

    def _one(self, snapshot: FinanceSnapshot, scenario: dict[str, Any]) -> ScenarioResult:
        latest = snapshot.periods[-1]
        p = FinancePeriod(
            period=latest.period,
            revenue=max(0.0, latest.revenue * (1 + float(scenario.get('revenue_delta', 0.0)))),
            cash_in=max(0.0, latest.cash_in * (1 + float(scenario.get('cash_in_delta', scenario.get('revenue_delta', 0.0))))),
            cash_out=max(0.0, latest.cash_out * (1 + float(scenario.get('cash_out_delta', 0.0))) + latest.ad_spend * float(scenario.get('ad_spend_delta', 0.0))),
            ad_spend=max(0.0, latest.ad_spend * (1 + float(scenario.get('ad_spend_delta', 0.0)))),
            gross_profit=max(0.0, latest.gross_profit * (1 + float(scenario.get('revenue_delta', 0.0)))),
            gross_margin=latest.gross_margin,
            cac=max(0.0, latest.cac * (1 + float(scenario.get('cac_delta', 0.0)))),
            ltv=max(0.0, latest.ltv * (1 + float(scenario.get('ltv_delta', 0.0)))),
            customers=latest.customers,
            orders=latest.orders,
            retention_rate=min(1.0, max(0.0, latest.retention_rate * (1 + float(scenario.get('retention_delta', 0.0))))),
            channel=latest.channel,
        )
        projected = FinanceSignalEngine().from_rows([p.to_dict()], company_id=snapshot.company_id, cash_balance=snapshot.cash_balance)
        diagnoses = CashflowDiagnosisEngine().diagnose(projected)
        score = CapitalEfficiencyEngine().score(projected, diagnoses)
        risk = 'high' if projected.runway_months < 3 or score.score < 40 else 'medium' if projected.runway_months < 6 or score.score < 58 else 'low'
        upside = projected.signals['revenue_growth_rate'] * 100
        action = score.decision
        if scenario.get('months') and projected.burn_rate > 0:
            months = float(scenario['months'])
            remaining_cash = snapshot.cash_balance - projected.burn_rate * months
            if remaining_cash < 0:
                action = 'RAISE_OR_CUT_COSTS_BEFORE_6_MONTHS'
                risk = 'high'
        return ScenarioResult(
            name=str(scenario.get('name', 'custom')),
            runway_months=round(projected.runway_months, 2),
            cash_risk=risk,
            growth_upside=round(upside, 2),
            capital_efficiency=score.score,
            recommended_action=action,
            projected={k: round(v, 4) for k, v in projected.signals.items()},
        )
