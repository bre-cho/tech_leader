---
description: "Use when editing frontend/src/pages/** to keep UI mapping, state handling, and API usage aligned with the root app contract."
name: "Frontend Pages Mapping"
applyTo: "frontend/src/pages/**/*.tsx,frontend/src/pages/**/*.ts"
---
# Frontend Pages Mapping

- Treat page components as the main mapping layer between UI state and API responses.
- Keep page-level data handling aligned with `frontend/src/lib/api.ts` and the backend schema it wraps.
- Do not add silent fallback logic that hides missing or renamed fields from the backend.
- Prefer explicit loading, empty, and error states instead of inferring success from partial data.
- Keep page UI behavior additive and predictable unless the task explicitly calls for a redesign.
- If a page needs new contract fields, update the API client and page mapping in the same patch.
- For DesignStudio specifically, preserve the current workflow-oriented presentation unless the request says otherwise.