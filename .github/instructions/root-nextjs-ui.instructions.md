---
description: "Use when editing the root Next.js app or shared UI components. Keeps the root app distinct from the separate Vite workspace and preserves API contract awareness."
name: "Root Next.js UI"
applyTo: "app/**/*.tsx,app/**/*.ts,components/**/*.tsx,components/**/*.ts"
---
# Root Next.js UI

- Treat the root `app/` and `components/` tree as the primary Next.js surface.
- Keep it separate from the `frontend/` Vite workspace; do not assume shared routing, build tooling, or env handling.
- When UI code consumes backend data, keep response shapes aligned with the backend schema and the frontend API contract rules.
- Avoid introducing ad-hoc data transforms that hide contract mismatches.
- Prefer additive UI changes and preserve existing visual/system patterns unless the task explicitly calls for a redesign.
- If a change affects the API contract, update the relevant frontend typing and contract references in the same patch.
- For broad UI changes, verify the root app build and typecheck paths before finishing.
