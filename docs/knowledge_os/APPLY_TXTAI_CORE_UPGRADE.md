# Apply txtai Core Upgrade for Agent 16

## Mục tiêu

Bản nâng cấp này lấy cảm hứng từ triết lý `txtai`: gom tìm kiếm ngữ nghĩa, tìm kiếm từ khóa, đồ thị liên kết, bộ nhớ dài hạn và hỏi đáp dữ liệu nội bộ vào một lõi gọn nhẹ.

Nó không phụ thuộc bắt buộc vào dịch vụ cloud. Mặc định chạy local bằng Python chuẩn và SQLite.

## Thành phần mới

```text
ai_trading_brain/knowledge_os/
├── text.py              # tách từ, chia đoạn, vector băm cục bộ
├── store.py             # SQLite store cho đoạn văn bản, đồ thị, memory
├── indexer.py           # quét project và xây chỉ mục
├── search.py            # tìm kiếm lai: từ khóa + vector + đồ thị
├── rag.py               # trả lời dựa trên kho tri thức nội bộ
├── runtime.py           # runtime API nội bộ
└── models.py            # data contracts

scripts/agent16_knowledge_os.py
```

## Cách chạy

### 1. Xây chỉ mục tri thức

```bash
python scripts/agent16_knowledge_os.py index --root . --out docs/runtime/knowledge-index.json
```

### 2. Hỏi dữ liệu nội bộ

```bash
python scripts/agent16_knowledge_os.py ask --query "quy trình release gate của agent 16 là gì" --out docs/runtime/knowledge-answer.json
```

### 3. Lưu mẫu chiến thắng

```bash
python scripts/agent16_knowledge_os.py remember --kind winner_pattern --score 91 --content "Hook đánh vào nỗi đau chi phí quảng cáo tăng tạo phản hồi tốt"
```

### 4. Gọi lại trí nhớ

```bash
python scripts/agent16_knowledge_os.py recall --kind winner_pattern
```

## Lý do nâng cấp MVP

Trước đây Agent 16 có nhiều module vận hành, nhưng thiếu một lõi đọc hiểu tri thức nội bộ thống nhất. Bản này giúp AI:

- không bị lạc ngữ cảnh khi dự án lớn
- tìm lại quyết định kiến trúc cũ
- hỏi đáp trên toàn bộ docs/source code
- lưu lại mẫu thành công/thất bại
- hỗ trợ tự sửa lỗi dựa trên bằng chứng trong project

## Chính sách an toàn

- Không tự chạy lệnh nguy hiểm.
- Không gửi dữ liệu ra ngoài.
- Không yêu cầu API key.
- SQLite lưu tại `.knowledge_os/knowledge.sqlite`.
- Có thể xóa chỉ mục bằng cách xóa thư mục `.knowledge_os/`.
