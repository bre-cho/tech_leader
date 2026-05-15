# VideoFlow → Tech Leader MVP Upgrade

## Mục tiêu

Bản nâng cấp này áp dụng `VideoFlow-main.zip` vào `tech_leader-main_2.zip` theo hướng an toàn, không phá kiến trúc gốc:

1. Lưu mã nguồn VideoFlow vào `packages/videoflow/` để làm nền renderer cục bộ.
2. Thêm lớp `lib/videoflow/` để chuyển Storyboard V31 thành timeline JSON kiểu VideoFlow.
3. Thêm API `POST /api/videoflow/compile` để tạo storyboard + timeline render preview.
4. Thêm cổng kiểm định timeline trước khi đưa vào render/merge.
5. Thêm test `npm run test:videoflow`.

## File đã thêm/sửa

- `packages/videoflow/` — mã nguồn VideoFlow local vendor.
- `lib/videoflow/types.ts` — hợp đồng timeline/layer bằng Zod.
- `lib/videoflow/storyboardAdapter.ts` — adapter Storyboard V31 → VideoFlow timeline.
- `lib/videoflow/verification.ts` — kiểm định layer, duration, canvas, caption, safe-zone.
- `lib/videoflow/index.ts` — export tập trung.
- `app/api/videoflow/compile/route.ts` — endpoint compile timeline.
- `tests/videoflow-adapter.test.ts` — test smoke cho adapter.
- `package.json` — thêm script `test:videoflow`.

## Cách chạy

```bash
npm install
npm run test:videoflow
npm run typecheck
npm run dev
```

Gọi API:

```bash
curl -X POST http://localhost:3000/api/videoflow/compile \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Luxury Beauty Short",
    "concept":"K-beauty fashion KOL commercial short",
    "platform":"youtube_shorts",
    "aspectRatio":"9:16",
    "targetDurationSec":35,
    "musicBpm":118,
    "provider":{"image":"hidream","video":"veo","motionFallback":"runway"}
  }'
```

## Luồng mới

```text
Storyboard V31 request
→ Rhythm / retention / provider payload compile
→ VideoFlowStoryboardAdapter
→ VideoFlow JSON timeline
→ VideoFlowVerificationGate
→ renderer/provider preview/merge pipeline
```

## Gợi ý bước tiếp theo

- Gắn timeline JSON này vào player DOM preview ở frontend.
- Khi cần render MP4 thật, cài package renderer chính thức hoặc build từ `packages/videoflow/src/renderer-server`.
- Gắn `videoFlowTimeline.provenance.inputHash` vào Artifact Contract để replay và drift check.

## Lưu ý TypeScript

`packages/videoflow/src` được giữ như mã nguồn tham chiếu upstream và đã được loại khỏi `tsconfig.json` của app chính. Lý do: upstream VideoFlow là monorepo workspace riêng, cần các alias package `@videoflow/*`, `mediabunny`, `playwright`. MVP hiện dùng adapter ổn định trong `lib/videoflow/`; khi muốn build renderer thật, hãy build VideoFlow như workspace riêng hoặc cài các package chính thức.
