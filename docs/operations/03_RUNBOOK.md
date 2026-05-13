# Runbook

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
cd backend
pytest -q
```

## Smoke API

```bash
curl -X POST http://localhost:8000/api/v1/design-studio/run \
  -H 'Content-Type: application/json' \
  -d '{"industry":"spa mỹ phẩm","product":"serum phục hồi da","audience":"phụ nữ 25-35","channel":"TikTok","goal":"bán hàng","brand_name":"Lumi Skin"}'
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```
