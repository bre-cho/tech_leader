# Smoke Test

```bash
python scripts/agent16_business_operating_mind.py . --out .agent16-business-os
cat .agent16-business-os/business_operating_report.md
```

The command exits non-zero when the Business OS gate is `NO-GO`, which is intended for CI blocking behavior.

For local inspection without CI failure handling:

```bash
python scripts/agent16_business_operating_mind.py . --out .agent16-business-os || true
```
