---
name: "Ship Backend Feature"
description: "Plan and implement a backend feature through the required workflow with law/verify/memory alignment, then produce merge-ready checklist evidence."
argument-hint: "Feature goal, affected modules, constraints, acceptance criteria"
agent: "agent"
---
Implement a backend feature using this repository's required operating workflow and governance constraints.

## Inputs
- Feature goal
- Affected files/modules
- API or schema changes
- Acceptance criteria

## Required Workflow
1. Define workflow impact across these steps:
   - target_define
   - research
   - plan
   - execute
   - verify
   - distill_to_skill
   - memory_update
   - winner_dna_update
2. Route implementation via runtime orchestration (not standalone shortcuts).
3. Update verification and promotion gate logic if behavior changes.
4. Update memory/context graph writes if the feature changes persisted knowledge.
5. Keep API contracts aligned with frontend usage when backend schema changes.

## Implementation Rules
- Prefer additive changes over broad refactors.
- Do not bypass governance gates.
- Keep compatibility unless breaking changes are explicitly requested.
- Link to existing docs instead of duplicating long guidance.

## Validation
- Run backend verification:
  - scripts/verify_backend.sh
- If API contract changed, include frontend impact notes and required type updates.

## Output
Return:
1. Summary of implemented change
2. Files changed and why
3. Law and verification impact
4. Checklist result against docs/patch/04_ADDING_NEW_FEATURE_RULE.md
5. Test/verification evidence
6. Follow-up tasks (if any)
