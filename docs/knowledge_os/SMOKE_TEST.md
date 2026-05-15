# Knowledge OS Smoke Test

```bash
python -m py_compile ai_trading_brain/knowledge_os/*.py scripts/agent16_knowledge_os.py
pytest -q
python scripts/agent16_knowledge_os.py index --root docs --out docs/runtime/knowledge-index.json
python scripts/agent16_knowledge_os.py ask --query "Agent 16 có chức năng gì" --out docs/runtime/knowledge-answer.json
```

Pass khi:

- py_compile không lỗi
- pytest pass
- file `docs/runtime/knowledge-index.json` có số chunks > 0
- file `docs/runtime/knowledge-answer.json` có answer + hits
