# Design-to-Video Multi-Agent MVP Pack

MVP patch pack cho hệ thống AI Design Studio → Image Scoring → Video Upsell → Storyboard → Offer → CRM → Analytics → Winner DNA Memory, dưới sự điều phối của Technical Lead Agent.

## Cấu trúc
- `docs/`: blueprint, agent contracts, workflow, API, DB, QA/release gate, lệnh Claude/Cursor/Copilot.
- `backend/`: FastAPI scaffold cho closed-loop agent runtime.
- `frontend/`: Next.js scaffold cho `/design-studio`.
- `alembic/versions/`: migration schema đề xuất.
- `scripts/`: audit + release gate wrapper.
- `.ai-workforce/`: prompts/commands/agent cards.

## Áp dụng vào repo hiện tại
Copy từng thư mục tương ứng vào repo MVP. Nếu repo đã có backend/frontend riêng, ưu tiên copy phần `docs/` trước, sau đó merge file-by-file theo patch plan.
