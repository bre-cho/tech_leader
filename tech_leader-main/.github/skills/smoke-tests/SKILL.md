---
name: smoke-tests
description: "Run the minimal verification sequence for the touched workspace surface and report pass/fail evidence before finishing. Use when you need the right test order for backend, root Next.js, or frontend Vite changes."
argument-hint: "Changed files, feature surface, and whether backend, root Next.js, or frontend Vite changed"
---
# Smoke Tests

Use this skill to choose the smallest verification set that covers the changed surface.

## When To Use
- Before finishing work that changed backend runtime, frontend API contracts, or UI code.
- When you need a consistent verification order for mixed workspace changes.

## Default Order
1. If backend runtime or governance changed, run `./scripts/verify_backend.sh`.
2. If the root Next.js app changed, run `npm run build` and `npm run typecheck` from the repository root.
3. If the `frontend/` Vite workspace changed, run `cd frontend && npm run build`.
4. If the task only touched docs or customization files, explain why code verification was not required.

## Checklist Asset
- Use [smoke checklist](assets/smoke-checklist.md) to capture which commands ran and whether each passed.

## Reporting
- State exactly which commands you ran.
- Report pass/fail status for each command.
- If something failed, give the shortest actionable fix path and stop before claiming completion.
- If multiple surfaces changed, include the sequence you used and why it was sufficient.

## Notes
- Do not skip backend verification for runtime or governance changes.
- Do not confuse the root Next.js app with the separate `frontend/` Vite workspace.
- Keep the output short and evidence-based.
