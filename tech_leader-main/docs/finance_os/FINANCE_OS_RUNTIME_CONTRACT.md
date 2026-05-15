# Finance OS Runtime Contract

## Input Contract

Mỗi dòng dữ liệu có thể là tháng hoặc channel-month:

```json
{
  "period": "2026-02",
  "channel": "meta_ads",
  "revenue": 9500,
  "cash_in": 9500,
  "cash_out": 12000,
  "ad_spend": 3800,
  "cac": 65,
  "ltv": 145,
  "customers": 110,
  "gross_margin": 0.52,
  "retention_rate": 0.39,
  "planned_budget": 3000,
  "actual_budget": 3800
}
```

## Decision Contract

AI CEO decision trả về:

- `mode`: `cash_protection | controlled_growth | optimize_before_scale | hold_and_learn`
- `authority`: quyền thực thi ngân sách
- `primary_bottlenecks`: diagnosis code
- `budget_actions`: channel -> action
- `scenario_risks`: scenario -> low/medium/high
- `guardrails`: điều kiện cấm scale
- `recommended_focus`: danh sách hành động ưu tiên

## Guardrails

1. Không scale budget nếu runway < 3 tháng.
2. Không scale paid growth nếu LTV/CAC < 3 nếu chưa approval.
3. Giảm channel ROI < 1 khi đang cash protection.
4. Memory chỉ ghi từ measured/simulated evidence.
