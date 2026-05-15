from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class FinancePeriod:
    period: str
    revenue: float = 0.0
    cash_in: float = 0.0
    cash_out: float = 0.0
    ad_spend: float = 0.0
    gross_profit: float = 0.0
    gross_margin: float = 0.0
    cac: float = 0.0
    ltv: float = 0.0
    customers: float = 0.0
    orders: float = 0.0
    retention_rate: float = 0.0
    channel: str = 'total'
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def net_cashflow(self) -> float:
        return self.cash_in - self.cash_out

    @property
    def burn_rate(self) -> float:
        return max(0.0, self.cash_out - self.cash_in)

    @property
    def roi(self) -> float:
        if self.ad_spend <= 0:
            return 0.0
        return (self.revenue - self.ad_spend) / self.ad_spend

    @property
    def ltv_cac_ratio(self) -> float:
        if self.cac <= 0:
            return 0.0
        return self.ltv / self.cac

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.update({
            'net_cashflow': round(self.net_cashflow, 4),
            'burn_rate': round(self.burn_rate, 4),
            'roi': round(self.roi, 4),
            'ltv_cac_ratio': round(self.ltv_cac_ratio, 4),
        })
        return data


@dataclass(frozen=True)
class FinanceSnapshot:
    company_id: str
    generated_at: str
    periods: list[FinancePeriod]
    cash_balance: float
    monthly_revenue: float
    previous_monthly_revenue: float
    total_revenue: float
    total_cash_in: float
    total_cash_out: float
    total_ad_spend: float
    average_cac: float
    average_ltv: float
    gross_margin: float
    burn_rate: float
    runway_months: float
    roi: float
    budget_variance: float
    signals: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data['periods'] = [p.to_dict() for p in self.periods]
        return data


class FinanceSignalEngine:
    """Transforms raw business finance data into auditable financial signals.

    Input supports either dictionaries or CSV rows. Required fields are intentionally
    flexible so MVP teams can ingest exported data from Stripe, Shopify, ads tools,
    or manual spreadsheets without building integrations first.
    """

    NUMERIC_FIELDS = {
        'revenue', 'cash_in', 'cash_out', 'ad_spend', 'gross_profit', 'gross_margin',
        'cac', 'ltv', 'customers', 'orders', 'retention_rate', 'cash_balance',
        'planned_budget', 'actual_budget'
    }

    def from_csv(self, path: str | Path, company_id: str = 'default') -> FinanceSnapshot:
        with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        return self.from_rows(rows, company_id=company_id)

    def from_json(self, path: str | Path, company_id: str = 'default') -> FinanceSnapshot:
        payload = json.loads(Path(path).read_text(encoding='utf-8'))
        if isinstance(payload, dict):
            company_id = str(payload.get('company_id', company_id))
            rows = payload.get('periods') or payload.get('rows') or []
            cash_balance = _num(payload.get('cash_balance'))
        else:
            rows = payload
            cash_balance = 0.0
        return self.from_rows(rows, company_id=company_id, cash_balance=cash_balance)

    def from_rows(self, rows: Iterable[dict[str, Any]], company_id: str = 'default', cash_balance: float | None = None) -> FinanceSnapshot:
        normalized = [self._normalize_row(r) for r in rows]
        normalized.sort(key=lambda r: r.period)
        if not normalized:
            normalized = [FinancePeriod(period=date.today().isoformat()[:7])]
        last = normalized[-1]
        prev = normalized[-2] if len(normalized) > 1 else FinancePeriod(period='previous')
        total_revenue = sum(p.revenue for p in normalized)
        total_cash_in = sum(p.cash_in for p in normalized)
        total_cash_out = sum(p.cash_out for p in normalized)
        total_ad_spend = sum(p.ad_spend for p in normalized)
        avg_cac = _weighted_average([(p.cac, p.customers) for p in normalized])
        avg_ltv = _weighted_average([(p.ltv, p.customers) for p in normalized])
        gross_profit = sum(p.gross_profit for p in normalized)
        gross_margin = gross_profit / total_revenue if total_revenue > 0 and gross_profit > 0 else _average([p.gross_margin for p in normalized if p.gross_margin > 0])
        inferred_cash_balance = cash_balance if cash_balance is not None and cash_balance > 0 else max(0.0, total_cash_in - total_cash_out)
        monthly_burn = max(0.0, last.cash_out - last.cash_in)
        runway = 999.0 if monthly_burn <= 0 else inferred_cash_balance / monthly_burn
        roi = 0.0 if total_ad_spend <= 0 else (total_revenue - total_ad_spend) / total_ad_spend
        planned = sum(_num(p.metadata.get('planned_budget')) for p in normalized)
        actual = sum(_num(p.metadata.get('actual_budget')) for p in normalized) or total_ad_spend
        budget_variance = 0.0 if planned <= 0 else (actual - planned) / planned
        signals = {
            'monthly_revenue': last.revenue,
            'previous_monthly_revenue': prev.revenue,
            'revenue_growth_rate': _growth(last.revenue, prev.revenue),
            'cash_in': last.cash_in,
            'cash_out': last.cash_out,
            'net_cashflow': last.net_cashflow,
            'burn_rate': monthly_burn,
            'runway_months': runway,
            'gross_margin': gross_margin,
            'ad_spend': last.ad_spend,
            'roi': roi,
            'cac': avg_cac,
            'ltv': avg_ltv,
            'ltv_cac_ratio': 0.0 if avg_cac <= 0 else avg_ltv / avg_cac,
            'budget_variance': budget_variance,
            'retention_rate': _weighted_average([(p.retention_rate, max(1.0, p.customers)) for p in normalized]),
        }
        return FinanceSnapshot(
            company_id=company_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            periods=normalized,
            cash_balance=inferred_cash_balance,
            monthly_revenue=last.revenue,
            previous_monthly_revenue=prev.revenue,
            total_revenue=total_revenue,
            total_cash_in=total_cash_in,
            total_cash_out=total_cash_out,
            total_ad_spend=total_ad_spend,
            average_cac=avg_cac,
            average_ltv=avg_ltv,
            gross_margin=gross_margin,
            burn_rate=monthly_burn,
            runway_months=runway,
            roi=roi,
            budget_variance=budget_variance,
            signals={k: round(float(v), 6) for k, v in signals.items()},
        )

    def _normalize_row(self, row: dict[str, Any]) -> FinancePeriod:
        clean = {str(k).strip().lower(): v for k, v in row.items()}
        period = str(clean.get('period') or clean.get('month') or clean.get('date') or date.today().isoformat()[:7])[:10]
        if len(period) >= 7:
            period = period[:7]
        revenue = _num(clean.get('revenue') or clean.get('sales') or clean.get('mrr'))
        cash_in = _num(clean.get('cash_in') or clean.get('inflow') or revenue)
        cash_out = _num(clean.get('cash_out') or clean.get('outflow') or clean.get('expenses'))
        ad_spend = _num(clean.get('ad_spend') or clean.get('marketing_spend') or clean.get('ads'))
        cogs = _num(clean.get('cogs') or clean.get('cost_of_goods_sold'))
        gross_profit = _num(clean.get('gross_profit')) or max(0.0, revenue - cogs) if cogs > 0 else _num(clean.get('gross_profit'))
        gross_margin = _num(clean.get('gross_margin'))
        if gross_margin > 1.0:
            gross_margin /= 100.0
        if gross_margin <= 0 and revenue > 0 and gross_profit > 0:
            gross_margin = gross_profit / revenue
        retention = _num(clean.get('retention_rate') or clean.get('retention'))
        if retention > 1.0:
            retention /= 100.0
        metadata = {k: _num(v) if k in self.NUMERIC_FIELDS else v for k, v in clean.items() if k not in {
            'period', 'month', 'date', 'revenue', 'sales', 'mrr', 'cash_in', 'inflow', 'cash_out', 'outflow', 'expenses',
            'ad_spend', 'marketing_spend', 'ads', 'gross_profit', 'gross_margin', 'cogs', 'cost_of_goods_sold', 'cac', 'ltv',
            'customers', 'orders', 'retention_rate', 'retention', 'channel'
        }}
        return FinancePeriod(
            period=period,
            revenue=revenue,
            cash_in=cash_in,
            cash_out=cash_out,
            ad_spend=ad_spend,
            gross_profit=gross_profit,
            gross_margin=gross_margin,
            cac=_num(clean.get('cac')),
            ltv=_num(clean.get('ltv')),
            customers=_num(clean.get('customers')),
            orders=_num(clean.get('orders')),
            retention_rate=retention,
            channel=str(clean.get('channel') or 'total'),
            metadata=metadata,
        )


def _num(value: Any) -> float:
    if value is None or value == '':
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(',', '').replace('$', '').replace('%', '')
    try:
        return float(text)
    except ValueError:
        return 0.0


def _average(values: list[float]) -> float:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else 0.0


def _weighted_average(values: list[tuple[float, float]]) -> float:
    weighted = [(v, max(0.0, w)) for v, w in values if v > 0]
    total_weight = sum(w for _, w in weighted)
    if total_weight <= 0:
        return _average([v for v, _ in weighted])
    return sum(v * w for v, w in weighted) / total_weight


def _growth(current: float, previous: float) -> float:
    if previous <= 0:
        return 1.0 if current > 0 else 0.0
    return (current - previous) / previous
