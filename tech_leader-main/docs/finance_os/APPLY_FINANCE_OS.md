# Finance OS Production Patch

Bản nâng cấp này thêm Finance Intelligence Layer thật cho Agent16 / AI Business OS:

- `FinanceSignalEngine`: ingest CSV/JSON, chuẩn hóa revenue, cashflow, CAC, LTV, burn, runway, gross margin, ROI, budget variance.
- `CashflowDiagnosisEngine`: phát hiện runway risk, growth efficiency collapse, budget leakage, margin compression, budget drift, retention/LTV risk.
- `CapitalEfficiencyEngine`: score capital efficiency 0-100 để AI CEO quyết định scale/hold/protect/stop.
- `BudgetAllocationOptimizer`: phân bổ ngân sách theo ROI, LTV/CAC, cash constraint và risk.
- `FinancialScenarioSimulator`: mô phỏng tăng ads, CAC tăng, revenue giảm, retention tăng, burn giữ nguyên 6 tháng.
- `FinancialMemoryStore`: lưu finance winner/risk pattern dạng JSONL.
- `FinanceOperatingRuntime`: chạy end-to-end từ dữ liệu tài chính đến quyết định AI CEO + execution plan.

## Cách chạy nhanh

```bash
python scripts/agent16_finance_os.py examples/finance_sample.csv --company-id demo --out .finance-os
```

Nếu chưa có file mẫu, tạo CSV như sau:

```csv
period,channel,revenue,cash_in,cash_out,ad_spend,cac,ltv,customers,gross_margin,retention_rate,planned_budget,actual_budget
2026-01,meta_ads,10000,10000,9500,3000,50,140,120,0.55,0.42,2800,3000
2026-02,meta_ads,9500,9500,12000,3800,65,145,110,0.52,0.39,3000,3800
2026-02,google_ads,7000,7000,5000,1200,32,160,90,0.58,0.46,1200,1200
```

## Output

- `.finance-os/finance_operating_report.json`
- `.finance-os/finance_operating_report.md`
- `.finance-os/financial_memory.jsonl`

## Verify

```bash
python -m py_compile ai_trading_brain/finance/*.py scripts/agent16_finance_os.py
pytest -q
```
