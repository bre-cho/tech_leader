# FASHION_BEAUTY_RUNTIME_V1_PATCH

## Mục tiêu

Nâng cấp `tech_leader-main` dựa trên 2 bộ ảnh người dùng đã gửi:

1. **Luxury Quiet Beauty / Chanel-like Editorial DNA**
   - trắng kem
   - nâu chocolate
   - ngọc trai
   - túi xách luxury
   - soft feminine editorial
   - quiet luxury commercial

2. **Hyper Feminine Fashion Motion / Miu-like Pastel Runtime**
   - peach / lavender / pastel pink
   - tóc chuyển động mạnh
   - fashion walk
   - kinetic pose
   - Gen Z luxury
   - TikTok / Xiaohongshu commerce energy

Patch này biến MVP thành:

```text
AI-Native Cinematic Fashion Intelligence Infrastructure
```

Không chỉ tạo ảnh/video, mà có thêm:

```text
Visual DNA
→ Emotional Perception Graph
→ Character Continuity Runtime
→ Fashion Motion Engine
→ Beauty Commerce Engine
→ Storyboard Runtime
→ Video Handoff
→ Winner DNA Memory
```

---

## Module backend mới

```text
backend/app/visual_fashion_runtime/
  __init__.py
  schemas.py
  visual_dna_extractor.py
  emotional_perception_graph.py
  character_continuity_runtime.py
  fashion_motion_engine.py
  beauty_commerce_engine.py
  storyboard_runtime.py
  winner_dna_memory.py
  orchestrator.py

backend/app/api/v1/fashion_beauty_runtime.py
```

---

## Module Next.js mới

```text
app/fashion-runtime/page.tsx
app/fashion-runtime/fashion-runtime.css
app/api/v1/fashion-runtime/[...path]/route.ts
components/fashion-runtime/FashionRuntimeStudio.tsx
lib/fashion-runtime-api.ts
types/fashion-runtime.ts
```

---

## Module Vite mới

```text
frontend/src/pages/FashionMovieStudio.tsx
frontend/src/fashion-runtime/runtime/fashionHandoffReceiver.ts
frontend/src/types/fashion-runtime.ts
frontend/src/styles/fashion-runtime.css
```

---

## API

```text
POST /api/v1/fashion-runtime/analyze
POST /api/v1/fashion-runtime/generate-storyboard
GET  /api/v1/fashion-runtime/taxonomy
```

---

## Kết quả chính

Từ brief đơn giản:

```text
Luxury K-beauty fashion campaign with peach lavender motion energy
```

Hệ thống tự tạo:

- Visual DNA
- Color palette
- Luxury perception score
- Fashion archetype
- Character continuity lock
- Motion language
- Beauty commerce positioning
- 12-scene storyboard
- sequential render policy
- Vite handoff payload
- Winner DNA memory payload
