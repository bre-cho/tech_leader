# Scenema Audio Voice Cloning Upgrade cho `tech_leader-main`

## Mục tiêu nâng cấp

Bản vá này thêm lớp provider `scenema_audio` vào `backend/app/tts_studio` để nâng cấp luồng audio voice cloning từ mock/IndexTTS payload sang Scenema Audio sidecar.

Scenema Audio hiện hỗ trợ zero-shot voice cloning bằng audio tham chiếu 10–20 giây, tạo giọng biểu cảm, giữ độ liền mạch khi đọc dài bằng cách chia đoạn, và hỗ trợ nhiều ngôn ngữ, gồm cả tiếng Việt trong UI mẫu. Nguồn tham khảo: Scenema Audio model card và GitHub chính thức.  
- Hugging Face: `ScenemaAI/scenema-audio`  
- GitHub: `ScenemaAI/scenema-audio`  
- Demo/product: `https://scenema.ai/audio`

## File đã thêm/sửa

```text
backend/app/tts_studio/contracts.py
backend/app/tts_studio/indextts_provider.py
backend/app/tts_studio/scenema_audio_provider.py
third_party/scenema-audio/
docs/SCENEMA_AUDIO_VOICE_CLONING_UPGRADE.md
backend/tests/test_scenema_audio_provider.py
```

## Cách chạy Scenema Audio sidecar

Scenema Audio nên chạy như dịch vụ GPU riêng, không nhúng model 22B trực tiếp vào backend chính.

```bash
cd third_party/scenema-audio
export HF_TOKEN=your_huggingface_token
ENABLE_GRADIO=1 docker compose up
```

Mặc định sidecar mở API ở:

```text
http://localhost:8000/generate
```

Nếu backend chính cũng chạy cổng 8000, hãy đổi cổng sidecar trong compose hoặc chạy backend ở cổng khác. Ví dụ:

```bash
export SCENEMA_AUDIO_URL=http://localhost:8010
```

## Biến môi trường backend

```bash
SCENEMA_AUDIO_URL=http://localhost:8000
SCENEMA_AUDIO_DRY_RUN=true
SCENEMA_AUDIO_TIMEOUT_S=900
```

- `SCENEMA_AUDIO_DRY_RUN=true`: không gọi GPU, chỉ xuất payload JSON để kiểm tra tích hợp.
- `SCENEMA_AUDIO_DRY_RUN=false`: gọi thật Scenema Audio và lưu WAV.

## Gọi API tạo voice cloned line

```bash
curl -X POST http://localhost:8000/api/v1/tts-studio/generate-line \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "demo_scenema_001",
    "provider": "scenema_audio",
    "line": {
      "line_id": "line_001",
      "speaker_id": "narrator",
      "text": "Xin chào, đây là bản đọc thử bằng giọng clone biểu cảm cho video thương mại.",
      "emotion": {"joy": 0.15, "calm": 0.25},
      "manual_emotion": true
    },
    "character": {
      "character_id": "char_narrator",
      "display_name": "Narrator",
      "voice_id": "voice_demo",
      "speaking_style": "Vietnamese female narrator, warm, cinematic, clear commercial delivery"
    },
    "voice": {
      "voice_id": "voice_demo",
      "display_name": "Reference Voice",
      "source_wav_path": "https://example.com/reference-voice.wav",
      "language": "vi",
      "metadata": {
        "gender": "female",
        "scene": "premium studio voiceover booth",
        "shot": "closeup",
        "pace": 1.08,
        "validate": false,
        "vc_steps": 25,
        "vc_cfg_rate": 0.5
      }
    }
  }'
```

Khi `SCENEMA_AUDIO_DRY_RUN=true`, kết quả là file payload JSON trong `/tmp/indextts-line`. Khi tắt dry-run, kết quả là file `.wav`.

## Luồng vận hành đề xuất

```text
Script line
→ EmotionVector
→ Character speaking_style
→ VoiceAsset metadata/reference voice
→ Scenema XML <speak> prompt
→ Scenema /generate sidecar
→ WAV take
→ TimelineBuilder
→ ExportMixService
→ LipDub / Video postprocess
```

## Quy tắc bảo mật và pháp lý

Chỉ clone giọng khi có quyền sử dụng audio tham chiếu. Nên lưu `voice_consent=true`, nguồn audio, thời gian cấp quyền và phạm vi sử dụng trong `VoiceAsset.metadata` trước khi chạy production.

## Kiểm thử

```bash
cd backend
pytest tests/test_scenema_audio_provider.py
```

Kiểm thử mặc định chạy ở dry-run nên không cần GPU và không tải model.
