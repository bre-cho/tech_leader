# V30 × AUTO STORYBOARD ENGINE V3 SALES UPGRADE

## Mục tiêu

Áp dụng `AUTO_STORYBOARD_ENGINE_V3_SALES_PATCH` vào `v30_storyboard_agent_lfw_runway_full_patch`.

V30 ban đầu mạnh ở:

```text
Setup → Backstage → Runway → After Party
160-shot fashion event storyboard
camera/motion/emotion/focus
provider batches
retention pacing
```

AUTO STORYBOARD ENGINE V3 bổ sung lớp:

```text
Product category detection
Sales mechanism routing
Hook / Desire / Trust / Proof / CTA
Product clarity scoring
Provider prompt compiler
Sales render queue
Sales verification gate
```

## Luồng mới

```text
V30 Fashion Event Storyboard
↓
Sales Engine V3
↓
Category Detection
↓
Sales Mechanism Detection
↓
Commercial Scene Builder
↓
Sales Shot Injection
↓
Provider Prompt Compiler
↓
Sales Verification Gate
↓
Render Queue
```

## Cơ chế bán hàng được hỗ trợ

```text
lip_desire
skin_transformation
sun_shield
ingredient_explosion
liquid_vortex
texture_proof
luxury_identity
human_emotion
mini_world_story
product_dominance
```

## API mới

```text
POST /api/storyboard/v30/sales-run
POST /api/storyboard/v30/sales-provider-batches
```

## Runtime mới

```text
lib/storyboard-v30/storyboardAgentRuntime.sales-upgraded.ts
lib/storyboard-v30-sales/
```

## Frontend panel mới

```text
components/storyboard-v30/SalesEngineV3Panel.tsx
```

## Cách gọi

```bash
curl -X POST http://localhost:3000/api/storyboard/v30/sales-run \
  -H "Content-Type: application/json" \
  -d @examples/v30_sales_lipstick_runway.json
```

## Test

```bash
tsx tests/v30-sales-upgraded.test.ts
```

## Apply vào UI V30

Trong `components/storyboard-v30/StoryboardV30Studio.tsx`, sau khi có `result`, thêm:

```tsx
import SalesEngineV3Panel from "@/components/storyboard-v30/SalesEngineV3Panel";

<SalesEngineV3Panel
  salesEngine={result.salesEngineV3}
  verification={result.verification}
  providerPayloads={result.providerPayloads}
/>
```

Đổi endpoint từ:

```text
/api/storyboard/v30/run
```

sang:

```text
/api/storyboard/v30/sales-run
```

nếu muốn bật sales layer.

## Kết quả

Storyboard Agent V30 sau nâng cấp không chỉ dựng phim runway, mà còn có thể biến runway/storyboard thành video bán hàng:

```text
Fashion event cinematic
+
Commercial hook
+
Product desire
+
Trust/proof
+
CTA
+
Render queue
```
