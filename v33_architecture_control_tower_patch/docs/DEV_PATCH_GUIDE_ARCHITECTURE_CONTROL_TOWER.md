# Dev Patch Guide — Architecture Control Tower

## Install

```bash
pip install -e services/architecture-observer
```

## Before AI patch

```bash
architecture-observer snapshot --repo . --out runtime/architecture-governance/snapshot_before.json
```

## After AI patch

```bash
architecture-observer compare --before runtime/architecture-governance/snapshot_before.json --repo . --out-dir runtime/architecture-governance
```

Exit codes:
- 0 = promote
- 1 = manual_review
- 2 = block

## Test

```bash
python -m pytest tests/test_architecture_observer.py -q
```
