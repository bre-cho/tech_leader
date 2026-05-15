# 02 — Frontend Patch Guide

## Route chính

`/design-studio`

## UI cần có

1. Business Form
2. Generate Image Concepts
3. Image Gallery
4. AI Score Panel
5. Upsell Video Recommendation
6. Video Storyboard Preview
7. Select Video Package
8. Winner DNA Badge

## API env

`.env`

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Tích hợp vào Next.js nếu repo chính dùng Next

Copy logic trong:

```text
frontend/src/pages/DesignStudio.tsx
frontend/src/lib/api.ts
```

sang:

```text
src/app/design-studio/page.tsx
src/lib/api.ts
```

Sau đó đổi `import` CSS theo hệ UI hiện tại.
