from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .budget_allocator import BudgetRecommendation
from .capital_efficiency import CapitalEfficiencyScore
from .cashflow_diagnosis import CashflowDiagnosis
from .finance_signal_engine import FinanceSnapshot


@dataclass(frozen=True)
class FinancialMemoryEvent:
    event_type: str
    key: str
    weight: float
    market_condition: str
    context: dict[str, Any]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FinancialMemoryStore:
    """Append-only JSONL memory for finance winners, failures, and decisions."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def build_events(
        self,
        snapshot: FinanceSnapshot,
        diagnoses: list[CashflowDiagnosis],
        capital_score: CapitalEfficiencyScore,
        budget: list[BudgetRecommendation],
    ) -> list[FinancialMemoryEvent]:
        condition = self._market_condition(snapshot, capital_score)
        events = [
            FinancialMemoryEvent(
                event_type='finance_state_snapshot',
                key=f'{snapshot.company_id}:{snapshot.generated_at}',
                weight=0.9 if capital_score.decision.startswith(('STOP', 'PROTECT')) else 0.65,
                market_condition=condition,
                context={'signals': snapshot.signals, 'capital_efficiency': capital_score.to_dict(), 'diagnoses': [d.to_dict() for d in diagnoses]},
                created_at=_now(),
            )
        ]
        for rec in budget:
            event_type = 'budget_winner_candidate' if rec.change_percent > 15 and rec.risk < 0.55 else 'budget_risk_pattern' if rec.change_percent < -15 else 'budget_hold_pattern'
            events.append(FinancialMemoryEvent(
                event_type=event_type,
                key=f'{snapshot.company_id}:{rec.channel}:{event_type}',
                weight=0.8 if event_type == 'budget_winner_candidate' else 0.55,
                market_condition=condition,
                context=rec.to_dict(),
                created_at=_now(),
            ))
        return events

    def append(self, events: list[FinancialMemoryEvent]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')

    def recall(self, event_type: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.path.open('r', encoding='utf-8') as f:
            for line in f:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event_type is None or row.get('event_type') == event_type:
                    rows.append(row)
        return rows[-limit:]

    def _market_condition(self, snapshot: FinanceSnapshot, score: CapitalEfficiencyScore) -> str:
        if snapshot.runway_months < 3:
            return 'cash_constrained'
        if score.decision == 'SCALE_CONTROLLED':
            return 'efficient_growth'
        if snapshot.signals.get('revenue_growth_rate', 0) < 0:
            return 'revenue_decline'
        return 'steady_state'


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
