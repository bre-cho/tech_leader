---
description: "Use when editing the separate Vite frontend workspace. Keeps Vite-specific build, env, and contract conventions distinct from the root Next.js app."
name: "Frontend Vite Workspace"
applyTo: "frontend/src/**/*,frontend/app/**/*"
---
# Frontend Vite Workspace

- Treat `frontend/` as a standalone Vite app with its own build and typecheck flow.
- Do not assume root Next.js routing, server components, or build behavior applies here.
- Keep API client code aligned with backend schema and avoid silent fallback logic that hides contract mismatches.
- Preserve the `VITE_API_BASE` and `/api/v1` assumptions used by the workspace.
- When changing UI mappings or request/response types, update the relevant frontend API contract references in the same patch.
- Prefer additive changes and keep workspace-specific styling and component patterns consistent with the existing Vite app.
- Before finishing frontend contract or UI changes, run `cd frontend && npm run build`.
