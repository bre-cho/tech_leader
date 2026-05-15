# Apply Engineering OS Upgrade

## Mục tiêu
Biến repo thành một AI Engineering Operating System có governance, context graph, phase planning, verification report, memory và reusable skills.

## Lệnh chạy nhanh

```bash
python scripts/engineering_os.py run "build backend API for finance signals" --repo .
```

Kết quả sinh ra:

```text
docs/runtime/context-graph.json
docs/runtime/phase-plan.md
docs/runtime/governance-decision.json
docs/runtime/verification-report.md
docs/runtime/engineering-memory.jsonl
```

## Workflow chuẩn

1. Cập nhật `docs/brief.md`, `docs/BRD.md`, `docs/master-plan.md`.
2. Chạy planner:
   ```bash
   python scripts/engineering_os.py plan "TASK" --repo .
   ```
3. Kiểm tra governance gate:
   ```bash
   python scripts/engineering_os.py gate "TASK" --repo .
   ```
4. Code theo plan.
5. Verify:
   ```bash
   python scripts/engineering_os.py verify "TASK" --repo .
   ```
6. Update changelog và memory.

## Nguyên tắc bắt buộc
- Không sửa production trực tiếp.
- Không refactor ngoài phạm vi task.
- Schema-breaking change phải có rollback và approval.
- Mọi feature phải có smoke test.
