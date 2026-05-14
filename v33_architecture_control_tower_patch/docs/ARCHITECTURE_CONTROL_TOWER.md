# V33 — Architecture Control Tower

## Mục tiêu

Nâng Technical Lead Agent thành **Architecture Control Tower**.

```text
AI Agent đề xuất patch
↓
CodeGraph Snapshot trước patch
↓
AI thực thi patch
↓
CodeGraph Snapshot sau patch
↓
Blast Radius Diff
↓
Architecture Drift Check
↓
Promotion Gate
```

## Module mới

```text
/services/architecture-observer
  code_graph_scanner.py
  dependency_mapper.py
  blast_radius_analyzer.py
  architecture_drift_detector.py
  ai_change_visualizer.py
  promotion_gate_guard.py

/runtime/architecture-governance
  snapshot_before.json
  snapshot_after.json
  blast_radius_report.json
  drift_report.json

/apps/admin
  Architecture Map
  Agent Change Viewer
  Blast Radius Dashboard
```

## Core Operating Law mới

```text
TARGET DEFINE
→ ARCHITECTURE SNAPSHOT
→ RESEARCH
→ PLAN
→ IMPACT PREVIEW
→ EXECUTE
→ BLAST RADIUS CHECK
→ VERIFY
→ PROMOTION GATE
→ MEMORY UPDATE
```

## CLI

```bash
pip install -e services/architecture-observer
architecture-observer snapshot --repo . --out runtime/architecture-governance/snapshot_before.json
architecture-observer compare --before runtime/architecture-governance/snapshot_before.json --repo . --out-dir runtime/architecture-governance
```

## Admin UI

```text
/apps/admin/app/architecture/page.tsx
POST /api/architecture/snapshot
POST /api/architecture/compare
```

## Promotion logic

- promote: score >= 85
- manual_review: score 65-84
- block: score < 65 hoặc drift/blast radius quá lớn
