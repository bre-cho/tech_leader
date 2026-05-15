# Mapping CodeNomad → Agent 16

CodeNomad cung cấp tư duy "buồng lái lập trình AI": nhiều phiên làm việc, kiểm soát lệnh, quản lý ngữ cảnh, session và giao diện điều phối. Agent 16 dùng phần lõi phù hợp nhất để nâng cấp MVP theo hướng vận hành thật.

| Ý tưởng CodeNomad | Agent 16 áp dụng |
|---|---|
| Session Management | `.codenomad_core/sessions.jsonl` lưu lịch sử phiên |
| Permission Center | `safety.py` + approval token |
| File System Browser | `context.py` quét cấu trúc dự án |
| Command Palette | `scripts/agent16_codenomad.py` CLI |
| SideCars / multi-agent workflow | Planner → Executor → Healer → Reporter |
| Rich message/status | `codenomad-runtime-report.md` |
| Self-healing from terminal | `healing.py` đọc lỗi và tạo kế hoạch sửa |

Điểm khác: Agent 16 không bê nguyên desktop UI. Bản này lấy "xương sống vận hành" để dùng được ngay trong repo Python/CLI hiện tại.
