# 04 — Provider Integration

MVP hiện dùng mock provider để chạy ngay.

## Image provider thật

Thay logic tại:

```text
backend/app/services/image_provider.py
```

Provider output contract:

```json
{
  "image_url": "",
  "provider": "openai|gemini|sdxl|flux",
  "prompt": "",
  "metadata": {}
}
```

## Video provider thật

Thay logic tại:

```text
backend/app/services/video_provider.py
```

Provider target:
- Veo
- Runway
- Kling
- Seedance

Video output contract:

```json
{
  "job_id": "",
  "provider": "",
  "status": "queued|running|succeeded|failed",
  "preview_url": "",
  "metadata": {}
}
```
