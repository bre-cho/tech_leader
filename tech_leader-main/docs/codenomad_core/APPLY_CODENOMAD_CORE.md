# Áp dụng CodeNomad Core cho Agent 16

Mục tiêu: biến Agent 16 thành trợ lý lập trình có quy trình rõ ràng: đọc ngữ cảnh dự án, lập kế hoạch, chạy lệnh an toàn, đọc lỗi terminal, đề xuất tự sửa lỗi và ghi báo cáo.

## 1. Thành phần được thêm

```text
ai_trading_brain/codenomad_core/
├── context.py        # quét cấu trúc dự án
├── planner.py        # lập kế hoạch thực thi
├── safety.py         # phân loại rủi ro lệnh
├── executor.py       # chạy lệnh qua cổng an toàn
├── healing.py        # tạo kế hoạch tự sửa lỗi từ log terminal
├── memory.py         # lưu lịch sử phiên làm việc
└── runtime.py        # vòng lặp vận hành chính

scripts/agent16_codenomad.py
```

## 2. Cách chạy nhanh

```bash
python scripts/agent16_codenomad.py context --repo .
python scripts/agent16_codenomad.py plan "audit codebase and suggest safe fixes" --repo .
python scripts/agent16_codenomad.py run "audit codebase and suggest safe fixes" --repo .
```

Mặc định là dry-run, chỉ mô phỏng lệnh để tránh phá dự án.

## 3. Chạy lệnh thật

Chỉ dùng cho lệnh đã kiểm tra an toàn:

```bash
python scripts/agent16_codenomad.py exec "python -m pytest -q" --repo . --execute
```

Lệnh rủi ro trung bình/cao cần token:

```bash
python scripts/agent16_codenomad.py exec "pip install -r requirements.txt" --repo . --execute --approval-token APPROVE_LOCAL_EXECUTION
```

## 4. Báo cáo sinh ra

```text
docs/runtime/codenomad-context.json
docs/runtime/codenomad-plan.md
docs/runtime/codenomad-runtime-report.md
docs/runtime/codenomad-healing-plan.md
.codenomad_core/sessions.jsonl
```

## 5. Nguyên tắc an toàn

- Không tự deploy.
- Không tự force push.
- Không chạy lệnh phá hệ thống.
- Không xóa test để làm xanh giả.
- Mọi lỗi phải có kế hoạch sửa và báo cáo nghiệm thu.
