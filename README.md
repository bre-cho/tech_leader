# Multi-Agent Image Design Workforce

This patch rebuilds Image Design Agent as a real multi-agent workforce.

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
./scripts/verify_workforce.sh
```

## Endpoint

```text
POST /api/v1/workforce/image-design/run
```
