# 01 — Backend Architecture

```text
backend/app
├── agents
├── api
├── context_graph
├── memory
├── models
├── runtime
├── schemas
└── services
```

## Runtime chuẩn

```text
Technical Lead Agent
↓
Planner
↓
Capability Router
↓
Execution Manager
↓
Retry Engine
↓
Verification Engine
↓
Promotion Gate
↓
Memory Update
```

## Core endpoint

`POST /api/v1/design-studio/run`

Input:

```json
{
  "industry": "spa",
  "product": "dịch vụ chăm sóc da",
  "audience": "phụ nữ 25-40",
  "channel": "Facebook",
  "goal": "bán hàng",
  "brand_name": "Glow Spa",
  "tone": "luxury trust"
}
```

Output gồm:
- business diagnosis
- image concepts
- image scores
- best concept
- upsell analysis
- video concept preview
- storyboard
- offer packages
- memory write result
