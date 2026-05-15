# Engineering OS Runtime Contract

## Input
- Task tự nhiên từ owner.
- Repo hiện tại.
- `AGENTS.md` và `/docs` làm long-term organizational memory.

## Runtime Loop

```text
Project Constitution
↓
Context Graph
↓
Planning Runtime
↓
Governance Gate
↓
Builder Execution
↓
Verification Layer
↓
Report + Memory Update
↓
Reusable Skills
```

## Governance Rules
- `blocked`: task có destructive/security critical action.
- `needs_human_approval`: migration/auth/security/deploy/payment/worker impact.
- `approved`: additive change, không có trigger rủi ro lớn.

## Verification Contract
- Python compile.
- Pytest nếu có tests.
- AGENTS.md present.
- Report lưu tại `docs/runtime/verification-report.md`.
