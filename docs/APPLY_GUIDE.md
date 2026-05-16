# APPLY GUIDE

## 1. Backend

Copy:

```bash
cp -r backend/app/visual_fashion_runtime <repo>/backend/app/
cp backend/app/api/v1/fashion_beauty_runtime.py <repo>/backend/app/api/v1/
```

Trong `backend/app/main.py` hoặc nơi include router:

```python
from app.api.v1.fashion_beauty_runtime import router as fashion_beauty_runtime_router
app.include_router(fashion_beauty_runtime_router, prefix="/api/v1")
```

Nếu repo đang dùng router tập trung:

```python
api_router.include_router(fashion_beauty_runtime_router)
```

Test:

```bash
curl -X POST http://localhost:8000/api/v1/fashion-runtime/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "brief":"Luxury K-beauty pastel fashion campaign with peach lavender motion energy",
    "target_duration":60,
    "provider":"kling",
    "planned_batch_size":6
  }'
```

---

## 2. Next.js

Copy:

```bash
cp -r app/fashion-runtime <repo>/app/
cp -r app/api/v1/fashion-runtime <repo>/app/api/v1/
cp -r components/fashion-runtime <repo>/components/
cp lib/fashion-runtime-api.ts <repo>/lib/
cp types/fashion-runtime.ts <repo>/types/
```

Mở:

```text
http://localhost:3000/fashion-runtime
```

ENV cần có:

```env
BACKEND_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_VIDEO_STUDIO_URL=http://localhost:5173
```

---

## 3. Vite

Copy:

```bash
cp frontend/src/pages/FashionMovieStudio.tsx <repo>/frontend/src/pages/
cp -r frontend/src/fashion-runtime <repo>/frontend/src/
cp frontend/src/types/fashion-runtime.ts <repo>/frontend/src/types/
cp frontend/src/styles/fashion-runtime.css <repo>/frontend/src/styles/
```

Thêm nhánh mount vào `frontend/src/main.tsx`:

```tsx
import FashionMovieStudio from './pages/FashionMovieStudio'

const params = new URLSearchParams(window.location.search)

if (params.has('fashion_handoff')) {
  root.render(<FashionMovieStudio />)
} else {
  root.render(<App />)
}
```

Nếu file đang render trực tiếp `DesignStudio`, thay `App` bằng component hiện tại.

---

## 4. Luật render an toàn

```text
planned_batch_size = số cảnh trong batch kế hoạch
max_concurrent_render = 1
execution_mode = sequential
```

Không render nhiều cảnh cùng lúc.
Scene trước xong mới chạy scene sau.

---

## 5. Dev checklist

- [ ] API backend trả về visual_dna
- [ ] API backend trả về storyboard 12 cảnh
- [ ] Next page gọi proxy `/api/v1/fashion-runtime/analyze`
- [ ] Vite nhận `fashion_handoff`
- [ ] Sequential render state chạy đúng
- [ ] Không dùng trực tiếp localhost:8000 trong browser
- [ ] Có winner DNA memory payload
