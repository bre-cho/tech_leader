from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .finance_signal_engine import FinanceSnapshot


@dataclass(frozen=True)
class CashflowDiagnosis:
    code: str
    severity: str
    confidence: float
    message: str
    causal_chain: list[str]
    evidence: dict[str, float]
    recommended_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CashflowDiagnosisEngine:
    """Detects finance bottlenecks from multiple signals, not single-rule alerts."""

    def diagnose(self, snapshot: FinanceSnapshot) -> list[CashflowDiagnosis]:
        s = snapshot.signals
        out: list[CashflowDiagnosis] = []
        if s['cash_in'] < s['cash_out'] and s['runway_months'] < 6:
            out.append(CashflowDiagnosis(
                'runway_risk', 'critical' if s['runway_months'] < 3 else 'high', 0.94,
                'Cash outflow is higher than cash inflow and runway is short.',
                ['cash_in < cash_out', 'negative net cashflow', 'runway pressure'],
                {'cash_in': s['cash_in'], 'cash_out': s['cash_out'], 'runway_months': s['runway_months']},
                ['freeze non-essential spend', 'prioritize high-ROI channels', 'review pricing and collection cycle'],
            ))
        if s['cac'] > 0 and s['ltv'] > 0 and s['ltv_cac_ratio'] < 3:
            out.append(CashflowDiagnosis(
                'growth_efficiency_collapse', 'high' if s['ltv_cac_ratio'] < 2 else 'medium', 0.9,
                'LTV/CAC is below healthy scaling threshold.',
                ['CAC rising or LTV weak', 'unit economics weak', 'paid growth unsafe'],
                {'cac': s['cac'], 'ltv': s['ltv'], 'ltv_cac_ratio': s['ltv_cac_ratio']},
                ['do not scale ads blindly', 'improve offer retention/LTV', 'cut channels with low contribution margin'],
            ))
        if s['ad_spend'] > 0 and s['revenue_growth_rate'] <= 0 and s['roi'] < 1:
            out.append(CashflowDiagnosis(
                'budget_leakage', 'high', 0.87,
                'Ad spend exists but revenue is flat/declining and ROI is weak.',
                ['ad spend active', 'revenue growth non-positive', 'low ROI'],
                {'ad_spend': s['ad_spend'], 'revenue_growth_rate': s['revenue_growth_rate'], 'roi': s['roi']},
                ['reduce spend on weak campaigns', 'route budget to proven channel/creative', 'run creative and funnel diagnosis before scale'],
            ))
        if s['gross_margin'] > 0 and s['gross_margin'] < 0.35:
            out.append(CashflowDiagnosis(
                'margin_compression', 'medium' if s['gross_margin'] >= 0.2 else 'high', 0.83,
                'Gross margin is below safe operating threshold.',
                ['gross margin weak', 'pricing/COGS problem', 'profitability pressure'],
                {'gross_margin': s['gross_margin']},
                ['review pricing', 'reduce COGS', 'bundle/upsell to lift margin'],
            ))
        if abs(s['budget_variance']) > 0.15:
            out.append(CashflowDiagnosis(
                'budget_variance_drift', 'medium', 0.78,
                'Actual budget differs materially from plan.',
                ['budget variance > 15%', 'planning drift', 'capital allocation risk'],
                {'budget_variance': s['budget_variance']},
                ['reconcile planned vs actual spend', 'update budget guardrails', 'require approval for overspend'],
            ))
        if s['retention_rate'] > 0 and s['retention_rate'] < 0.35 and s['ltv'] > 0:
            out.append(CashflowDiagnosis(
                'retention_ltv_risk', 'medium', 0.76,
                'Retention is weak, limiting LTV and capital efficiency.',
                ['low retention', 'lower LTV', 'weaker CAC payback'],
                {'retention_rate': s['retention_rate'], 'ltv': s['ltv']},
                ['build CRM retention flows', 'improve onboarding', 'create upsell/re-engagement offers'],
            ))
        if not out:
            out.append(CashflowDiagnosis(
                'financial_state_stable', 'ok', 0.7,
                'No critical financial bottleneck detected from provided signals.',
                ['cashflow stable', 'no critical thresholds triggered'],
                {'runway_months': s['runway_months'], 'roi': s['roi'], 'ltv_cac_ratio': s['ltv_cac_ratio']},
                ['continue monitoring', 'test controlled growth scenarios', 'store winner finance pattern'],
            ))
        return out
