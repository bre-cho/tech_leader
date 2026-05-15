# 03 — Memory & Winner DNA

## Winner DNA schema

```json
{
  "industry": "",
  "visual_type": "",
  "hook": "",
  "offer": "",
  "conversion_score": 0,
  "upsell_rate": 0,
  "storyboard_pattern": ""
}
```

## Recall rule

```text
When same industry appears:
→ inject previous winners into new planning context
```

## MVP storage

SQLite file:

```text
backend/data/agentic_mvp.db
```

Production nên đổi sang Postgres + pgvector.
