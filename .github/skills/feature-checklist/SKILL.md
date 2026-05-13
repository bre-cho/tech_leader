---
name: feature-checklist
description: 'Run pre-merge backend feature checklist for operating law, verification gate, runtime boundaries, tests, docs, and contract alignment. Use before opening or merging backend PRs.'
argument-hint: 'Changed files, feature intent, and whether API/schema changed'
---
# Feature Checklist

Use this skill to validate backend feature readiness before merge.

## When To Use
- Before creating a backend PR
- When reviewing runtime/governance edits
- When adding new agent/runtime behavior
- When API/schema changes may affect frontend

## Checklist
1. Workflow coverage
- Confirm required lifecycle presence:
  - target_define
  - research
  - plan
  - execute
  - verify
  - distill_to_skill
  - memory_update
  - winner_dna_update

2. Governance and gate safety
- Ensure no bypass path around verification or promotion gate.
- Ensure law trace and verification checks both influence promotion status.

3. Runtime boundaries
- Confirm design-to-video flow stays in backend/app/runtime and backend/app/governance.
- Avoid standalone shortcut paths that skip orchestrator sequencing.

4. Feature rule compliance
- Validate against docs/patch/04_ADDING_NEW_FEATURE_RULE.md.
- Use [PR checklist template](./assets/pr-checklist.md) to capture pass/fail evidence.

5. Contract alignment
- If backend schema changed, confirm frontend API typings are updated or explicitly planned.

6. Verification
- Run scripts/verify_backend.sh.
- Report failing checks with file-level fix guidance.

## Output
Provide:
- Passed checklist items
- Missing checklist items
- Blocking issues before merge
- Suggested minimal fixes
- Verification command results summary

## References
- docs/patch/04_ADDING_NEW_FEATURE_RULE.md
- backend/app/governance/operating_law.py
- backend/app/runtime/orchestrator.py
- backend/app/runtime/verification.py
