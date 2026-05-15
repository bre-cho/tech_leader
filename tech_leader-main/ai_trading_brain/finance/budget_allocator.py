from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .capital_efficiency import CapitalEfficiencyScore
from .finance_signal_engine import FinanceSnapshot


@dataclass(frozen=True)
class ChannelPerformance:
    channel: str
    revenue: float
    ad_spend: float
    cac: float
    ltv: float
    roi: float
    risk: float


@dataclass(frozen=True)
class BudgetRecommendation:
    channel: str
    action: str
    current_budget: float
    recommended_budget: float
    change_percent: float
    reason: str
    risk: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BudgetAllocationOptimizer:
    """Allocates budget by ROI, unit economics, cash constraint, and risk."""

    def allocate(self, snapshot: FinanceSnapshot, capital_score: CapitalEfficiencyScore, next_budget: float | None = None) -> list[BudgetRecommendation]:
        channels = self._channel_performance(snapshot)
        total_current = sum(c.ad_spend for c in channels)
        if next_budget is None:
            if capital_score.decision == 'SCALE_CONTROLLED':
                next_budget = total_current * 1.2
            elif capital_score.decision == 'HOLD_AND_OPTIMIZE':
                next_budget = total_current
            elif capital_score.decision == 'PROTECT_CASH_FIX_BOTTLENECKS':
                next_budget = total_current * 0.75
            else:
                next_budget = total_current * 0.5
        if not channels or next_budget <= 0:
            return [BudgetRecommendation('all', 'hold', total_current, 0.0, -100.0 if total_current else 0.0, 'No valid channel data or budget unavailable.', 1.0)]
        weights: dict[str, float] = {}
        for c in channels:
            unit = c.ltv / c.cac if c.cac > 0 and c.ltv > 0 else 1.0
            quality = max(0.0, c.roi) * 0.55 + min(unit / 4, 1.5) * 0.35 + (1 - c.risk) * 0.10
            if capital_score.decision.startswith('PROTECT') or capital_score.decision.startswith('STOP'):
                quality *= 0.65 if c.roi < 1 else 1.0
            weights[c.channel] = max(0.01, quality)
        total_weight = sum(weights.values())
        out: list[BudgetRecommendation] = []
        for c in channels:
            rec = next_budget * weights[c.channel] / total_weight
            change = 0.0 if c.ad_spend <= 0 else (rec - c.ad_spend) / c.ad_spend * 100
            if change > 15:
                action = f'scale_{round(change)}_percent'
            elif change < -15:
                action = f'reduce_{abs(round(change))}_percent'
            else:
                action = 'hold'
            reason = f'ROI={round(c.roi,2)}, LTV/CAC={round(c.ltv / c.cac,2) if c.cac else 0}, risk={round(c.risk,2)}, capital_decision={capital_score.decision}'
            out.append(BudgetRecommendation(c.channel, action, round(c.ad_spend, 2), round(rec, 2), round(change, 2), reason, round(c.risk, 3)))
        return sorted(out, key=lambda r: r.recommended_budget, reverse=True)

    def _channel_performance(self, snapshot: FinanceSnapshot) -> list[ChannelPerformance]:
        grouped: dict[str, dict[str, float]] = {}
        for p in snapshot.periods:
            ch = p.channel or 'total'
            g = grouped.setdefault(ch, {'revenue': 0.0, 'ad_spend': 0.0, 'customers': 0.0, 'ltv_sum': 0.0, 'cac_sum': 0.0, 'n': 0.0})
            g['revenue'] += p.revenue
            g['ad_spend'] += p.ad_spend
            g['customers'] += p.customers
            g['ltv_sum'] += p.ltv
            g['cac_sum'] += p.cac
            g['n'] += 1
        out = []
        for ch, g in grouped.items():
            if ch == 'total' and len(grouped) > 1:
                continue
            roi = 0.0 if g['ad_spend'] <= 0 else (g['revenue'] - g['ad_spend']) / g['ad_spend']
            cac = g['cac_sum'] / g['n'] if g['n'] else 0.0
            ltv = g['ltv_sum'] / g['n'] if g['n'] else 0.0
            risk = 0.2
            if roi < 1:
                risk += 0.35
            if cac > 0 and ltv > 0 and ltv / cac < 3:
                risk += 0.25
            if g['ad_spend'] <= 0:
                risk += 0.1
            out.append(ChannelPerformance(ch, g['revenue'], g['ad_spend'], cac, ltv, roi, min(1.0, risk)))
        if not out:
            out.append(ChannelPerformance('total', snapshot.total_revenue, snapshot.total_ad_spend, snapshot.average_cac, snapshot.average_ltv, snapshot.roi, 0.4))
        return out
