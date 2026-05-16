# Review Checklist - Patch Backend + UI

Tai lieu nay dung de review nhanh trong 5-10 phut truoc khi commit.

- Backend diff: [reports/patch_backend.diff](reports/patch_backend.diff)
- UI diff: [reports/patch_ui.diff](reports/patch_ui.diff)

## 1) Backend Checklist

### API Contract
- [ ] Xac nhan shape response cua Creative OS route on dinh va dong bo voi UI mapping.
- [ ] Kiem tra ten field khong bi drift: project_id, scenes/storyboard, planned_batch_size, max_concurrent_render, execution_mode.
- [ ] Kiem tra provider khong hop le tra loi ro rang (HTTP 400).

### Routing
- [ ] Router da duoc include vao app chinh.
- [ ] Prefix route dung theo /api/v1 + /creative-os, khong xung dot route cu.

### Typing + Safe Runtime
- [ ] Concurrency bi khoa ve 1 o schema/runtime queue.
- [ ] Logic tinh scene_count va batch phu hop voi duration + provider profile.

### Build Risk
- [x] Python compile cho file backend moi da pass.
- [ ] Smoke test endpoint nhanh:
- [ ] GET /api/v1/creative-os/provider-profiles
- [ ] POST /api/v1/creative-os/projects/{project_id}/plan-storyboard
- [ ] GET /api/v1/creative-os/projects/{project_id}/render-steps

## 2) UI Checklist

### API Contract Mapping
- [ ] Type Creative OS tren Next/Vite dong bo voi backend schema.
- [ ] Payload handoff tu Next sang Vite giu dung field quan trong.

### Routing + Wiring
- [ ] Route Next workflows hoat dong: /workflows
- [ ] Vite entrypoint nhan handoff query param va render dung trang.

### Typing
- [ ] Khong co loi type o cac file moi.
- [ ] Khong co mapping an loi contract (fallback che mat schema mismatch).

### Build Risk
- [x] Root typecheck da pass.
- [x] Root build da pass.
- [x] Frontend Vite build da pass.
- [ ] Manual check 2 luong:
- [ ] Mo trang Next workflows
- [ ] Bam Open Vite Video Studio va xac nhan scene/batch hien thi dung

## 3) Sign-off

- Reviewer:
- Ngay review:
- Ket qua tong:
- [ ] GO commit
- [ ] Need fixes before commit

## 4) Quick Notes

- Risk chinh (neu co):
- File can follow-up:
- Ghi chu cho lan patch tiep theo:
