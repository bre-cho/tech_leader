# Technical Changelog - Phase 4 Additive Sync

Ngay: 2026-05-15
Nhanh gon cho review/commit. Pham vi theo huong additive, khong overwrite hang loat.

## Nhom 1 - Root UI Brain Layout Sync
Muc tieu: dong bo giao dien root app voi bo cuc brain-main, giu route hien co.

Files:
- app/layout.tsx
- app/page.tsx
- app/globals.css
- components/BrainShell.tsx

Thay doi chinh:
- Ap dung shell layout co sidebar, topbar, card grid.
- Chuan hoa noi dung trang chu theo bo cuc Agent16 control tower.
- Ho tro responsive cho desktop/mobile trong stylesheet moi.

Tac dong hanh vi:
- Khong doi contract API backend.
- Khong doi route hien co cua root Next.js app.

## Nhom 2 - Commercial Creative API Call Hardening
Muc tieu: giu trai nghiem trang commercial khi proxy noi bo loi.

Files:
- app/commercial-creative/page.tsx

Thay doi chinh:
- Giu duong goi proxy noi bo truoc.
- Them fallback goi truc tiep backend qua NEXT_PUBLIC_API_BASE neu proxy that bai.
- Giu xu ly loi hien thi cho nguoi dung.

Tac dong hanh vi:
- Khong doi payload request.
- Tang do on dinh khi moi truong local/codespaces khac nhau.

## Nhom 3 - Winner DNA SQLite Safety
Muc tieu: ngan loi insert vao SQLite khi storyboard_pattern la list/object.

Files:
- backend/app/memory/winner_dna.py

Thay doi chinh:
- Chuyen storyboard_pattern thanh chuoi JSON truoc khi ghi DB neu khong phai string.

Tac dong hanh vi:
- Khong doi schema bang winner_dna.
- Giu nguyen logic threshold, duplicate check, payload_json.

## Nhom 4 - Backend Deprecation Cleanup (Khong doi behavior)
Muc tieu: giam canh bao deprecation trong test/verify backend.

Files:
- backend/app/main.py
- backend/app/compound_os_mvp/main.py
- backend/app/compound_os_mvp/db.py
- backend/app/compound_os_mvp/services/creative_graph.py
- backend/app/schemas/artifact.py
- backend/app/creative_os_mvp/core/config.py
- backend/app/vendor/veo_poster_backend_packages/apps_api/core/config.py
- backend/app/vendor/veo_poster_backend_packages/apps_api/schemas/core.py
- backend/app/vendor/kol_drama_runtime/drama/schemas/dialogue_subtext.py
- backend/app/vendor/kol_drama_runtime/drama/schemas/power_shift.py
- backend/app/vendor/kol_drama_runtime/drama/schemas/drama_memory.py
- backend/app/vendor/kol_drama_runtime/drama/schemas/drama_state.py

Thay doi chinh:
- Thay startup on_event bang lifespan trong cac app FastAPI.
- Thay datetime.utcnow bang datetime.now(UTC) theo cach tuong duong UTC naive khi can.
- Chuyen class Config sang ConfigDict/SettingsConfigDict cho Pydantic v2.

Tac dong hanh vi:
- Giu nguyen luong startup DB va middleware.
- Giu nguyen model validation semantics from_attributes.
- Khong doi endpoint public.

## Nhom 5 - TypeScript Scope Stabilization
Muc tieu: typecheck root app on dinh trong workspace co nhieu surface.

Files:
- tsconfig.json

Thay doi chinh:
- Dieu chinh ignoreDeprecations phu hop toolchain hien tai.
- Exclude frontend va tech_leader-main khoi pham vi root typecheck.

Tac dong hanh vi:
- Khong doi runtime behavior.
- Giam false-fail khi typecheck root Next.js app.

## Verification Evidence
Lenh da chay:
- npm run typecheck
- npm run build
- ./scripts/verify_backend.sh

Ket qua cuoi:
- typecheck: PASS
- build: PASS
- verify_backend: PASS (17 passed, 0 warnings)

Log tham chieu:
- backend_verify.log
- backend_verify_after_phase3.log

## Ghi chu Review/Commit
Goi y tach commit theo nhom de review de hon:
1. UI brain layout + commercial fallback
2. winner_dna sqlite safety
3. deprecation cleanup backend
4. tsconfig scope stabilization
