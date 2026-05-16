# GO/NO-GO 2 Phut - Pre-Commit Gate

Su dung tai buoi chot nhanh truoc commit.

- Scope backend: [reports/patch_backend.diff](reports/patch_backend.diff)
- Scope UI: [reports/patch_ui.diff](reports/patch_ui.diff)

## A. Critical Gate (bat buoc)

1. Build va typecheck
- [ ] Root typecheck pass
- [ ] Root build pass
- [ ] Frontend Vite build pass

2. API + Routing
- [ ] Route backend Creative OS truy cap duoc duoi /api/v1/creative-os/*
- [ ] Route Next /workflows render duoc trang Control Plane
- [ ] Vite nhan handoff query param va hien thi scene/batch

3. Contract
- [ ] Field handoff khop: project_id, storyboard/scenes, planned_batch_size, max_concurrent_render, execution_mode
- [ ] Khong co doi ten field public gay contract drift

4. Safety
- [ ] max_concurrent_render bi khoa = 1
- [ ] Queue render theo sequential mode

## B. Decision

- [ ] GO (du dieu kien commit)
- [ ] NO-GO (can sua truoc commit)

## C. Fast Note (toi da 3 dong)

- Ly do neu NO-GO:
- File can sua gap:
- Owner follow-up:
