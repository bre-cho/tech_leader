# Agent 16 Production Runbook

Agent 16 is not a skeleton. It performs real repository operations:

- Detects monorepo topology and runtime layers
- Builds Context Graph entities/edges from AST and imports
- Scans syntax, JSON contracts, secrets, mock leakage, live execution safety
- Validates runtime with compileall/pytest/npm/alembic when present
- Applies conservative safe fixes only
- Emits Markdown + JSON audit reports
- Enforces GO / REVIEW / NO-GO release gate

## Run full audit
```bash
python scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md
```

## Enforce release gate in CI
```bash
python scripts/agent16_release_gate.py reports/agent16_audit_report.json
```

## What auto-fix will do
- Create missing `__init__.py`
- Normalize line endings/trailing whitespace
- Create `reports/`, `context_graph/`, `.ai-workforce/commands/`
- Create Agent 16 command file

## What auto-fix will not do automatically
- It will not change live trading logic
- It will not bypass Risk Guard
- It will not hide failing tests
- It will not rotate secrets for you
