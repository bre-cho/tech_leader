# 05 — Smoke Tests

## Health

```bash
curl http://localhost:8000/api/v1/health
```

## Run Design Studio

```bash
curl -X POST http://localhost:8000/api/v1/design-studio/run \
  -H "Content-Type: application/json" \
  -d '{
    "industry":"spa",
    "product":"dịch vụ chăm sóc da",
    "audience":"phụ nữ 25-40",
    "channel":"Facebook",
    "goal":"bán hàng",
    "brand_name":"Glow Spa",
    "tone":"luxury trust"
  }'
```

## Check Winner DNA

```bash
curl http://localhost:8000/api/v1/memory/winner-dna
```
