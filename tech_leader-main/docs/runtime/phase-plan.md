# Phase Plan — build governed autonomous engineering organization

## Goal
Deliver a governed, verified engineering change for: build governed autonomous engineering organization

## Selected Skills
- create-page.skill

## Files to Modify
- `CHANGELOG.md`
- `docs/master-plan.md`
- `AGENTS.md`
- `scripts/context_graph_builder.py`
- `scripts/engineering_os.py`
- `tests/test_agent16_techlead.py`
- `tests/test_engineering_os.py`
- `ai_trading_brain/techlead/graph_builder.py`
- `ai_trading_brain/finance/financial_memory.py`
- `ai_trading_brain/engineering_os/__init__.py`
- `ai_trading_brain/engineering_os/models.py`
- `ai_trading_brain/engineering_os/context_graph.py`
- `ai_trading_brain/engineering_os/skills.py`
- `ai_trading_brain/engineering_os/planner.py`
- `ai_trading_brain/engineering_os/governance.py`
- `ai_trading_brain/engineering_os/verification.py`
- `ai_trading_brain/engineering_os/memory.py`
- `ai_trading_brain/engineering_os/runtime.py`
- `docs/engineering_os/APPLY_ENGINEERING_OS.md`
- `docs/engineering_os/RUNTIME_CONTRACT.md`

## Dependency Impact
- Context graph must be rebuilt before code changes
- Tests touching modified modules must be run

## Migration Impact
No schema migration detected from task text

## Risks
- Context drift if docs are stale
- Architecture drift if unrelated refactor occurs

## Rollback Plan
- Keep patch additive where possible
- Revert changed files from VCS if verification fails
- For migrations, include down migration before approval

## Execution Steps
### 1. Read constitution and project memory
- Owner: Planner Agent
- Risk: low
- Files:
  - `AGENTS.md`
  - `docs/brief.md`
  - `docs/BRD.md`
  - `docs/master-plan.md`
- Actions:
  - Load project constraints
  - Identify acceptance criteria
  - Confirm architecture boundaries
- Verification:
  - Context files exist or are generated
  - Task is mapped to explicit goal

### 2. Build engineering context graph
- Owner: Context Graph Agent
- Risk: medium
- Files:
  - `CHANGELOG.md`
  - `docs/master-plan.md`
  - `AGENTS.md`
  - `scripts/context_graph_builder.py`
  - `scripts/engineering_os.py`
  - `tests/test_agent16_techlead.py`
  - `tests/test_engineering_os.py`
  - `ai_trading_brain/techlead/graph_builder.py`
  - `ai_trading_brain/finance/financial_memory.py`
  - `ai_trading_brain/engineering_os/__init__.py`
- Actions:
  - Scan modules, tests, docs, workflows
  - Detect dependency impact
  - Export runtime graph JSON
- Verification:
  - context-graph.json generated
  - High-risk files listed

### 3. Implement additive patch only
- Owner: Builder Agent
- Risk: medium
- Files:
  - `CHANGELOG.md`
  - `docs/master-plan.md`
  - `AGENTS.md`
  - `scripts/context_graph_builder.py`
  - `scripts/engineering_os.py`
  - `tests/test_agent16_techlead.py`
  - `tests/test_engineering_os.py`
  - `ai_trading_brain/techlead/graph_builder.py`
  - `ai_trading_brain/finance/financial_memory.py`
  - `ai_trading_brain/engineering_os/__init__.py`
  - `ai_trading_brain/engineering_os/models.py`
  - `ai_trading_brain/engineering_os/context_graph.py`
  - `ai_trading_brain/engineering_os/skills.py`
  - `ai_trading_brain/engineering_os/planner.py`
  - `ai_trading_brain/engineering_os/governance.py`
  - `ai_trading_brain/engineering_os/verification.py`
  - `ai_trading_brain/engineering_os/memory.py`
  - `ai_trading_brain/engineering_os/runtime.py`
  - `docs/engineering_os/APPLY_ENGINEERING_OS.md`
  - `docs/engineering_os/RUNTIME_CONTRACT.md`
- Actions:
  - Apply smallest safe change
  - Avoid unrelated refactors
  - Preserve public contracts
- Verification:
  - No unrelated files changed
  - New/changed behavior has tests

### 4. Run verification gate
- Owner: QA Agent
- Risk: medium
- Files:
  - `tests/`
  - `docs/runtime/verification-report.md`
- Actions:
  - Run py_compile
  - Run pytest
  - Run configured smoke tests
  - Capture outputs
- Verification:
  - All required checks pass or report blockers

### 5. Report and update organizational memory
- Owner: Memory Agent
- Risk: low
- Files:
  - `CHANGELOG.md`
  - `docs/changelogs/`
  - `docs/runtime/engineering-memory.jsonl`
- Actions:
  - Write changelog
  - Write verification report
  - Append memory event
- Verification:
  - Memory event contains task, decision, checks, rollback

## Manual Verification
- Review generated phase plan
- Inspect changed files
- Run smoke command from report
- Approve release gate before deploy
