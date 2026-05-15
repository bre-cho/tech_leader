# APPLY — Agent16 System Audit & Governance Intelligence Layer

## Module added
- `ai_trading_brain/system_audit/`
- `ai_trading_brain/graphs/`
- `ai_trading_brain/memory_governance/`
- `ai_trading_brain/workforce/`
- `ai_trading_brain/strategic_cognition/`

## Scripts
```bash
python scripts/agent16_system_audit.py --root .
python scripts/agent16_graph_integrity_check.py --root .
python scripts/agent16_trustgraph_audit.py --root .
python scripts/agent16_memory_consistency_audit.py --root .
python scripts/agent16_workforce_contract_check.py --root .
python scripts/agent16_release_gate_full.py --root .
```

## Tests
```bash
python -m pytest -q tests/test_system_audit_inventory.py tests/test_context_graph_integrity.py tests/test_trustgraph_orchestration.py tests/test_agent_memory_topology.py tests/test_artifact_lineage_graph.py tests/test_replay_determinism.py tests/test_workforce_contracts.py tests/test_cross_agent_state.py tests/test_economic_cognition_flow.py tests/test_release_gate_full.py
```

## Output
Full audit report is written to:

`docs/runtime/agent16-system-audit-report.json`

## Release rule
- GO: no P0 blockers.
- NO-GO: runtime/static/trust/artifact lineage critical failure.
