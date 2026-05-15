from __future__ import annotations

import subprocess
import time
from pathlib import Path
from .models import CommandResult, utc_now
from .safety import classify_command


def run_command(command: str, repo_root: str | Path = ".", dry_run: bool = True, approval_token: str | None = None, timeout: int = 60) -> CommandResult:
    started = utc_now()
    t0 = time.time()
    risk = classify_command(command)
    if risk.level == "blocked":
        return CommandResult(command, "denied", None, "", risk.reason, started, utc_now(), int((time.time() - t0) * 1000), risk.level, "Command bị chặn vì có nguy cơ phá hệ thống.")
    if dry_run:
        return CommandResult(command, "skipped", None, f"DRY RUN: {command}\nRisk: {risk.level} — {risk.reason}", "", started, utc_now(), int((time.time() - t0) * 1000), risk.level)
    if risk.requires_approval and approval_token != "APPROVE_LOCAL_EXECUTION":
        return CommandResult(command, "denied", None, "", f"Approval required: {risk.reason}", started, utc_now(), int((time.time() - t0) * 1000), risk.level, "Thêm --approval-token APPROVE_LOCAL_EXECUTION nếu bạn đã kiểm tra lệnh.")
    try:
        proc = subprocess.run(command, cwd=str(Path(repo_root).resolve()), shell=True, text=True, capture_output=True, timeout=timeout)
        status = "executed" if proc.returncode == 0 else "failed"
        hint = None if proc.returncode == 0 else healing_hint(proc.stderr + "\n" + proc.stdout)
        return CommandResult(command, status, proc.returncode, proc.stdout, proc.stderr, started, utc_now(), int((time.time() - t0) * 1000), risk.level, hint)
    except subprocess.TimeoutExpired as exc:
        return CommandResult(command, "failed", 124, exc.stdout or "", exc.stderr or "timeout", started, utc_now(), int((time.time() - t0) * 1000), risk.level, "Tăng timeout hoặc tách command thành bước nhỏ hơn.")
    except Exception as exc:
        return CommandResult(command, "failed", 1, "", str(exc), started, utc_now(), int((time.time() - t0) * 1000), risk.level, "Kiểm tra quyền truy cập, shell hoặc đường dẫn repo.")


def healing_hint(output: str) -> str:
    lower = output.lower()
    if "modulenotfounderror" in lower or "cannot find module" in lower:
        return "Thiếu dependency hoặc sai import path; kiểm tra requirements/package và PYTHONPATH."
    if "syntaxerror" in lower or "unexpected token" in lower:
        return "Có lỗi cú pháp; mở file/line trong log, sửa cú pháp rồi chạy lại compile/test."
    if "assert" in lower or "failed" in lower:
        return "Test fail; đọc assertion, xác định expected/actual rồi sửa logic hoặc cập nhật test nếu yêu cầu thay đổi đúng."
    if "permission denied" in lower:
        return "Thiếu quyền file/lệnh; không dùng sudo tự động, hãy xử lý quyền thủ công."
    if "timeout" in lower:
        return "Command treo hoặc quá lâu; tách nhỏ hoặc tăng timeout."
    return "Cần phân tích log chi tiết; ưu tiên sửa nguyên nhân gốc, không bỏ qua test."
