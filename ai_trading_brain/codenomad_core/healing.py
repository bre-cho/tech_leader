from __future__ import annotations

import re
from pathlib import Path


def build_healing_plan(last_report_path: str | Path) -> str:
    path = Path(last_report_path)
    if not path.exists():
        return "# CodeNomad Healing Plan\n\nKhông tìm thấy runtime report. Hãy chạy command trước rồi tạo healing plan.\n"
    text = path.read_text(encoding="utf-8", errors="ignore")
    actions: list[str] = []
    if "ModuleNotFoundError" in text or "Cannot find module" in text:
        actions.append("Kiểm tra dependency thiếu và import path. Ưu tiên thêm dependency vào file quản lý package thay vì cài thủ công không kiểm soát.")
    if "SyntaxError" in text or "unexpected token" in text:
        actions.append("Mở đúng file/line báo lỗi cú pháp, sửa tối thiểu, chạy lại py_compile/typecheck.")
    if "AssertionError" in text or re.search(r"\bFAILED\b", text):
        actions.append("Đọc expected/actual trong test fail, sửa logic nghiệp vụ trước, không xóa test để pass giả.")
    if "timeout" in text.lower():
        actions.append("Tách command dài thành bước nhỏ, thêm timeout rõ ràng, kiểm tra vòng lặp vô hạn.")
    if not actions:
        actions.append("Không nhận diện pattern lỗi phổ biến. Cần review thủ công stdout/stderr trong report.")
    lines = ["# CodeNomad Healing Plan", "", "## Hành động đề xuất"]
    lines += [f"- {a}" for a in actions]
    lines += ["", "## Quy tắc an toàn", "- Không tự động xóa file hoặc reset git.", "- Không bỏ qua test bằng cách comment assertion.", "- Mỗi sửa đổi phải có rollback và test lại."]
    return "\n".join(lines) + "\n"
