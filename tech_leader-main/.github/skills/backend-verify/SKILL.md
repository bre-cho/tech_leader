---
name: backend-verify
description: "Run the backend verification workflow and report evidence. Use when you need to standardize scripts/verify_backend.sh and summarize pass/fail results."
argument-hint: "Changed backend files, runtime impact, and whether you need a verification summary"
---
# Backend Verify

Use this skill when backend runtime, governance, or feature changes need the standard verification pass.

## When To Use
- After editing backend runtime, governance, memory, or API contract code.
- When you need a concise verification summary for merge readiness.

## Standard Command
- Run `./scripts/verify_backend.sh` from the repository root.

## Checklist Asset
- Use [verify checklist](assets/verify-checklist.md) to record the command result and any failure details.

## Reporting
- State the command you ran.
- Report whether it passed or failed.
- If it failed, include the shortest actionable fix path and stop before claiming success.
- If the change also affects frontend contract shape, call out the follow-up frontend verification that is still needed.

## Notes
- Do not substitute a narrower command for backend runtime or governance changes.
- Keep the result short, factual, and evidence-based.
