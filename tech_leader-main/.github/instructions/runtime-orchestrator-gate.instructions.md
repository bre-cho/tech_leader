---
description: "Use when editing orchestrator, verification, or operating-law files that decide runtime sequencing, memory writes, or promotion gates."
name: "Runtime Orchestrator Gate"
applyTo: "backend/app/runtime/orchestrator.py,backend/app/runtime/verification.py,backend/app/governance/operating_law.py"
---
# Runtime Orchestrator and Gate

- Keep the required lifecycle fixed and complete:
  - target_define
  - research
  - plan
  - execute
  - verify
  - distill_to_skill
  - memory_update
  - winner_dna_update
- Do not introduce any path that marks promotion as passed without both law trace and verification checks succeeding.
- If you change the runtime sequence, update the orchestrator, verification engine, and operating law together.
- Keep memory updates and context graph writes explicit when runtime behavior changes.
- Preserve the existing required context entities and relation shape when touching workflow persistence.
- Prefer additive changes and avoid bypass-oriented helpers or shortcut execution paths.
