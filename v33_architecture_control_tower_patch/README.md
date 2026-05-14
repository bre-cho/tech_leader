# V33 — Architecture Control Tower Patch

CodeBoarding-style Architecture Visual Guard Layer cho MVP.

## Includes

- CodeGraph scanner
- Dependency mapper
- Blast radius analyzer
- Architecture drift detector
- AI change visualizer
- Promotion gate guard
- Admin dashboard
- API routes
- GitHub Action CI gate
- Tests + docs

## Quick start

```bash
pip install -e services/architecture-observer
architecture-observer snapshot --repo . --out runtime/architecture-governance/snapshot_before.json
architecture-observer compare --before runtime/architecture-governance/snapshot_before.json --repo . --out-dir runtime/architecture-governance
python -m pytest tests/test_architecture_observer.py -q
```
