# Mapping txtai → Agent 16

| Ý tưởng từ txtai | Áp dụng vào Agent 16 |
|---|---|
| Dense + sparse search | Tìm kiếm lai: từ khóa + vector băm local |
| Graph network | Đồ thị liên kết thuật ngữ trong docs/source |
| SQL integration | SQLite knowledge store |
| RAG pipeline | Hỏi đáp trên tài liệu nội bộ |
| Local-first | Không cần cloud/API key |
| Workflow | CLI index/ask/remember/recall |
| Agent memory | Lưu winner/failure/runtime memory |

## Kết quả

Agent 16 được nâng từ hệ có nhiều module riêng lẻ thành hệ có `bộ nhớ tri thức trung tâm`.

Flow mới:

```text
Source Code + Docs
↓
Knowledge Index
↓
Hybrid Search
↓
Context Retrieval
↓
AI Planning / Debugging / Marketing Decision
↓
Memory Update
```
