---
description: "Use when editing backend runtime flow, orchestrator logic, planner/router/verification, or promotion gate behavior. Enforces no bypass of verify and gate in backend/app/runtime files."
name: "Backend Runtime Guard"
applyTo: "backend/app/runtime/**/*.py"
---
# Backend Runtime Guard

- Do not bypass verification or promotion gate paths.
- Keep the mandatory law trace lifecycle intact:
  - target_define
  - research
  - plan
  - execute
  - verify
  - distill_to_skill
  - memory_update
  - winner_dna_update
- If you add or reorder runtime steps, update:
  - backend/app/governance/operating_law.py
  - backend/app/runtime/orchestrator.py
  - backend/app/runtime/verification.py
- Runtime features must be routed through orchestrator flow, not standalone ad-hoc agent calls.
- New runtime outputs must preserve existing response contracts consumed by frontend unless coordinated updates are included.
- Promotion gate status must remain driven by both law trace and verification checks.
- If a new feature affects memory or context graph, include explicit write path updates and verification checks.
- Prefer additive changes. Avoid broad refactors in runtime unless explicitly requested.
- Before finishing, run backend verification:
  - scripts/verify_backend.sh
