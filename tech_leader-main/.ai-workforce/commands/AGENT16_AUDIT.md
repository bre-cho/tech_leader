# AGENT16_AUDIT

Run:

```bash
python scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md
```

Rules: fix P0 first, then P1, never bypass Risk Guard for live trading.
