# Agent 16 — TrustGraph Context Graph Audit Report

**Repo:** `/workspaces/tech_leader`
**Release Gate:** **NO-GO**

## Executive Summary
Agent 16 đã quét repo thật, dựng Context Graph (3245 entities, 4554 edges), phát hiện P0=1, P1=8, P2=94, P3=0. Safe auto-fix applied=68. Release gate hiện tại: NO-GO. Với robot chạy tiền thật, chỉ được live khi gate=GO.

## Blocking Errors P0

1. **P0 / security-secret** — `backend/app/vendor/veo_poster_backend_packages/apps_api/core/config.py`
   - Vấn đề: Potential hard-coded secret/token detected.
   - Hướng sửa: Di chuyển secret sang env/secret manager, rotate key nếu đã commit.
   - Evidence: `{'match_start': 122}`

## High Risk P1

1. **P1 / inventory** — `.`
   - Vấn đề: Missing agent runtime.
   - Hướng sửa: Add at least one of: ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']
   - Evidence: `{'expected_any': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']}`
2. **P1 / inventory** — `.`
   - Vấn đề: Missing runtime governance.
   - Hướng sửa: Add at least one of: ['ai_trading_brain/governance.py']
   - Evidence: `{'expected_any': ['ai_trading_brain/governance.py']}`
3. **P1 / inventory** — `.`
   - Vấn đề: Missing observability.
   - Hướng sửa: Add at least one of: ['reports', 'backend/main.py']
   - Evidence: `{'expected_any': ['reports', 'backend/main.py']}`
4. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'agent runtime', 'expected_any': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']}`
5. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'governance', 'expected_any': ['ai_trading_brain/governance.py']}`
6. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'memory', 'expected_any': ['ai_trading_brain/memory_engine.py']}`
7. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'backend api', 'expected_any': ['backend/main.py']}`
8. **P1 / runtime-validation** — `.`
   - Vấn đề: Runtime check failed: pytest
   - Hướng sửa: Chạy `pytest -q` và sửa lỗi trước release gate.
   - Evidence: `{'cmd': 'pytest -q', 'stdout_tail': "our test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_patch_v23_v25_infra.py:6: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n_______________ ERROR collecting backend/tests/test_workforce.py _______________\nImportError while importing test module '/workspaces/tech_leader/backend/tests/test_workforce.py'.\nHint: make sure your test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_workforce.py:2: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n=========================== short test summary info ============================\nERROR backend/tests/test_commercial_intelligence.py\nERROR backend/tests/test_design_studio.py\nERROR backend/tests/test_hidream_v27.py\nERROR backend/tests/test_infrastructure_runtime.py\nERROR backend/tests/test_patch03_creative_os_mvp.py\nERROR backend/tests/test_patch04_creative_infrastructure_mvp.py\nERROR backend/tests/test_patch06_compound_os_mvp.py\nERROR backend/tests/test_patch_v23_v25_infra.py\nERROR backend/tests/test_workforce.py\n!!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!!\n9 errors in 3.05s\n"}`

## Graph Integrity Report

1. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'agent runtime', 'expected_any': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']}`
2. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'governance', 'expected_any': ['ai_trading_brain/governance.py']}`
3. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'memory', 'expected_any': ['ai_trading_brain/memory_engine.py']}`
4. **P1 / context-graph** — `.`
   - Vấn đề: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'backend api', 'expected_any': ['backend/main.py']}`
5. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:__future__', 'count': 346}`
6. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:pathlib', 'count': 108}`
7. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:datetime', 'count': 38}`
8. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:hashlib', 'count': 24}`
9. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:json', 'count': 77}`
10. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:typing', 'count': 214}`
11. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:pydantic', 'count': 58}`
12. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:sqlalchemy', 'count': 28}`
13. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:sqlalchemy.orm', 'count': 59}`
14. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:fastapi', 'count': 53}`
15. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:os', 'count': 28}`
16. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:uuid', 'count': 63}`
17. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:enum', 'count': 16}`
18. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:dataclasses', 'count': 46}`
19. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:sys', 'count': 16}`
20. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:argparse', 'count': 15}`
21. **P2 / context-graph** — `.`
   - Vấn đề: Graph risk signal: high_coupling_import
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P2', 'type': 'high_coupling_import', 'module': 'module:ai_trading_brain.system_audit.common', 'count': 18}`

## Memory Consistency Audit

✅ Không có mục trong nhóm này.

## Runtime / CI Validation

1. **P1 / runtime-validation** — `.`
   - Vấn đề: Runtime check failed: pytest
   - Hướng sửa: Chạy `pytest -q` và sửa lỗi trước release gate.
   - Evidence: `{'cmd': 'pytest -q', 'stdout_tail': "our test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_patch_v23_v25_infra.py:6: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n_______________ ERROR collecting backend/tests/test_workforce.py _______________\nImportError while importing test module '/workspaces/tech_leader/backend/tests/test_workforce.py'.\nHint: make sure your test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_workforce.py:2: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n=========================== short test summary info ============================\nERROR backend/tests/test_commercial_intelligence.py\nERROR backend/tests/test_design_studio.py\nERROR backend/tests/test_hidream_v27.py\nERROR backend/tests/test_infrastructure_runtime.py\nERROR backend/tests/test_patch03_creative_os_mvp.py\nERROR backend/tests/test_patch04_creative_infrastructure_mvp.py\nERROR backend/tests/test_patch06_compound_os_mvp.py\nERROR backend/tests/test_patch_v23_v25_infra.py\nERROR backend/tests/test_workforce.py\n!!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!!\n9 errors in 3.05s\n"}`
2. **P2 / runtime-validation** — `.`
   - Vấn đề: Runtime check failed: npm_build
   - Hướng sửa: Chạy `npm run build --if-present` và sửa lỗi trước release gate.
   - Evidence: `{'cmd': 'npm run build --if-present', 'stderr_tail': " ⨯ accounts/page.tsx doesn't have a root layout. To fix this error, make sure every page has a root layout.\nStatic worker exited with code: 1 and signal: null\n", 'stdout_tail': "\n> agentic-creative-operating-environment@1.0.0 build\n> next build\n\nAttention: Next.js now collects completely anonymous telemetry regarding usage.\nThis information is used to shape Next.js' roadmap and prioritize features.\nYou can learn more, including how to opt-out if you'd not like to participate in this anonymous program, by visiting the following URL:\nhttps://nextjs.org/telemetry\n\n   ▲ Next.js 15.1.4\n\n   Creating an optimized production build ...\n"}`

## Security Drift

1. **P0 / security-secret** — `backend/app/vendor/veo_poster_backend_packages/apps_api/core/config.py`
   - Vấn đề: Potential hard-coded secret/token detected.
   - Hướng sửa: Di chuyển secret sang env/secret manager, rotate key nếu đã commit.
   - Evidence: `{'match_start': 122}`

## File-by-file Patch Plan

1. **P1 / patch-plan** — `.`
   - Vấn đề: Patch required for inventory: Missing agent runtime.
   - Hướng sửa: Add at least one of: ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']
   - Evidence: `{'expected_any': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']}`
2. **P1 / patch-plan** — `.`
   - Vấn đề: Patch required for inventory: Missing runtime governance.
   - Hướng sửa: Add at least one of: ['ai_trading_brain/governance.py']
   - Evidence: `{'expected_any': ['ai_trading_brain/governance.py']}`
3. **P1 / patch-plan** — `.`
   - Vấn đề: Patch required for inventory: Missing observability.
   - Hướng sửa: Add at least one of: ['reports', 'backend/main.py']
   - Evidence: `{'expected_any': ['reports', 'backend/main.py']}`
4. **P0 / patch-plan** — `backend/app/vendor/veo_poster_backend_packages/apps_api/core/config.py`
   - Vấn đề: Patch required for security-secret: Potential hard-coded secret/token detected.
   - Hướng sửa: Xóa secret khỏi repo, dùng ENV/secret manager, rotate key.
   - Evidence: `{'match_start': 122}`
5. **P1 / patch-plan** — `.`
   - Vấn đề: Patch required for context-graph: Graph risk signal: missing_layer
   - Hướng sửa: Review graph risk signal and patch the referenced layer.
   - Evidence: `{'severity': 'P1', 'type': 'missing_layer', 'layer': 'agent runtime', 'expected_any': ['ai_trading_brain/brain_runtime.py', 'ai_trading_brain/unified_trade_pipeline.py']}`
6. **P1 / patch-plan** — `.`
   - Vấn đề: Patch required for runtime-validation: Runtime check failed: pytest
   - Hướng sửa: Chạy command trong evidence, sửa lỗi đầu tiên theo stderr_tail.
   - Evidence: `{'cmd': 'pytest -q', 'stdout_tail': "our test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_patch_v23_v25_infra.py:6: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n_______________ ERROR collecting backend/tests/test_workforce.py _______________\nImportError while importing test module '/workspaces/tech_leader/backend/tests/test_workforce.py'.\nHint: make sure your test modules/packages have valid Python names.\nTraceback:\n/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\nbackend/tests/test_workforce.py:2: in <module>\n    from app.main import app\nE   ModuleNotFoundError: No module named 'app.main'\n=========================== short test summary info ============================\nERROR backend/tests/test_commercial_intelligence.py\nERROR backend/tests/test_design_studio.py\nERROR backend/tests/test_hidream_v27.py\nERROR backend/tests/test_infrastructure_runtime.py\nERROR backend/tests/test_patch03_creative_os_mvp.py\nERROR backend/tests/test_patch04_creative_infrastructure_mvp.py\nERROR backend/tests/test_patch06_compound_os_mvp.py\nERROR backend/tests/test_patch_v23_v25_infra.py\nERROR backend/tests/test_workforce.py\n!!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!!\n9 errors in 3.05s\n"}`

## Business Operating Mind

Business OS State: `NO-GO`
Business OS Top Opportunity: `Fix P0 correctness blockers`

## Safe Auto-fixes Applied

1. **INFO / safe-autofix** — `backend/alembic/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
2. **INFO / safe-autofix** — `backend/alembic/versions/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
3. **INFO / safe-autofix** — `backend/app/commercial_intelligence/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
4. **INFO / safe-autofix** — `backend/app/engines/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
5. **INFO / safe-autofix** — `backend/app/workforce/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
6. **INFO / safe-autofix** — `backend/app/compound_os_mvp/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
7. **INFO / safe-autofix** — `backend/app/creative_infra_mvp/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
8. **INFO / safe-autofix** — `backend/.venv/lib/python3.12/site-packages/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
9. **INFO / safe-autofix** — `backend/app/workforce/agents/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
10. **INFO / safe-autofix** — `backend/app/compound_os_mvp/core/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
11. **INFO / safe-autofix** — `backend/app/compound_os_mvp/services/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
12. **INFO / safe-autofix** — `backend/app/creative_infra_mvp/services/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
13. **INFO / safe-autofix** — `backend/app/creative_infra_mvp/agents/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
14. **INFO / safe-autofix** — `backend/app/creative_infra_mvp/api/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
15. **INFO / safe-autofix** — `backend/app/vendor/kol_storyboard_engine/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
16. **INFO / safe-autofix** — `backend/app/vendor/kol_render_runtime/render/assembly/executors/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
17. **INFO / safe-autofix** — `backend/app/vendor/kol_render_runtime/render/assembly/vision/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
18. **INFO / safe-autofix** — `backend/app/vendor/kol_drama_runtime/drama/timeline/engines/__init__.py`
   - Vấn đề: Created missing __init__.py.
   - Hướng sửa: Đã tạo để ổn định import.
19. **INFO / safe-autofix** — `context_graph/risk_signals.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
20. **INFO / safe-autofix** — `context_graph/graph_summary.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
21. **INFO / safe-autofix** — `frontend/package.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
22. **INFO / safe-autofix** — `backend/artifacts/hidream/hidream_1778757993_c84ad3b057/replay_contract.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
23. **INFO / safe-autofix** — `backend/artifacts/hidream/hidream_1778758064_c3ac0fb57e/replay_contract.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
24. **INFO / safe-autofix** — `backend/tests/test_patch_v26_beauty.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
25. **INFO / safe-autofix** — `backend/app/runtime/verification.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
26. **INFO / safe-autofix** — `backend/app/api/v1/architecture_control_tower.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
27. **INFO / safe-autofix** — `backend/app/creative_infra_mvp/api/beauty_patches.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
28. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_backend_packages/packages/campaign_intelligence/engines.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
29. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_backend_packages/packages/campaign_intelligence/__init__.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
30. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_backend_packages/apps_api/creative_intelligence.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
31. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_backend_packages/apps_api/models/creative_intelligence.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
32. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_backend_packages/apps_api/schemas/creative_intelligence.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
33. **INFO / safe-autofix** — `backend/app/vendor/veo_poster_intelligence/poster-production/orchestrator.ts`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
34. **INFO / safe-autofix** — `backend/app/vendor/kol_storyboard_engine/provider_adapters/prompt_normalizer.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
35. **INFO / safe-autofix** — `backend/app/vendor/kol_storyboard_engine/provider_adapters/factory.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
36. **INFO / safe-autofix** — `backend/app/vendor/kol_storyboard_engine/provider_adapters/veo_adapter.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
37. **INFO / safe-autofix** — `backend/app/vendor/kol_storyboard_engine/provider_adapters/types.py`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
38. **INFO / safe-autofix** — `.github/instructions/root-nextjs-ui.instructions.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
39. **INFO / safe-autofix** — `.github/instructions/runtime-orchestrator-gate.instructions.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
40. **INFO / safe-autofix** — `.github/instructions/frontend-vite-workspace.instructions.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
41. **INFO / safe-autofix** — `.github/instructions/frontend-pages-mapping.instructions.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
42. **INFO / safe-autofix** — `.github/skills/backend-verify/SKILL.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
43. **INFO / safe-autofix** — `.github/skills/backend-verify/assets/verify-checklist.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
44. **INFO / safe-autofix** — `.github/skills/smoke-tests/SKILL.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
45. **INFO / safe-autofix** — `.github/skills/smoke-tests/assets/smoke-checklist.md`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
46. **INFO / safe-autofix** — `storage/test-v29-1/v29_1_identity_beauty_runtime_plan_4c54d61d3ccd.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
47. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_9d5f4acbf59c.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
48. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_560271cb117e.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
49. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_13f7a9bdf4be.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
50. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_9984320bd056.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
51. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_b09cf506d945.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
52. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_a2d488918b9d.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
53. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_e9c9aef9e25b.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
54. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_1f52d35f3c20.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
55. **INFO / safe-autofix** — `storage/v29-beauty-perception/v29_beauty_perception_plan_2ebd9406ffdc.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
56. **INFO / safe-autofix** — `storage/beauty-commerce-v28/beauty_commerce_v28_plan_14fe81db3cb8.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
57. **INFO / safe-autofix** — `docs/runtime/context-graph.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
58. **INFO / safe-autofix** — `docs/runtime/codenomad-context.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
59. **INFO / safe-autofix** — `docs/runtime/agent16-system-audit-report.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
60. **INFO / safe-autofix** — `docs/runtime/knowledge-answer.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
61. **INFO / safe-autofix** — `docs/runtime/governance-decision.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
62. **INFO / safe-autofix** — `docs/runtime/knowledge-index.json`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
63. **INFO / safe-autofix** — `lib/beauty-avatar/beautyAvatarGenerator.ts`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
64. **INFO / safe-autofix** — `app/commercial-creative/page.tsx`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
65. **INFO / safe-autofix** — `app/api/beauty-avatar/create/route.ts`
   - Vấn đề: Normalized line endings/trailing whitespace.
   - Hướng sửa: Không thay đổi logic.
66. **INFO / safe-autofix** — `reports`
   - Vấn đề: Created runtime directory.
   - Hướng sửa: Dùng cho audit reports/context graph.
67. **INFO / safe-autofix** — `.ai-workforce/commands`
   - Vấn đề: Created runtime directory.
   - Hướng sửa: Dùng cho audit reports/context graph.
68. **INFO / safe-autofix** — `.ai-workforce/commands/AGENT16_AUDIT.md`
   - Vấn đề: Created Agent 16 command file.
   - Hướng sửa: Claude/Cursor/Copilot can reuse this.

## Direct Commands for Claude Code / Cursor / Copilot

### Claude Code
```bash
python scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md
python scripts/context_graph_builder.py . --out context_graph
python -m compileall ai_trading_brain backend scripts
python scripts/agent16_business_operating_mind.py . --out .agent16-business-os
pytest -q
Fix P0 first, then P1. Do not refactor unrelated architecture.
```
### Cursor
```bash
Open reports/agent16_audit_report.md
Patch only Blocking Errors P0/P1 with file-by-file minimal changes.
Run python scripts/agent16_audit.py . --runtime after each patch batch.
```
### Copilot
```bash
Use AGENTS.md as workspace policy.
Generate tests for every patched production module.
Never add broker live execution without Risk Guard preflight and idempotency.
```
### Local CI
```bash
mkdir -p reports context_graph
python scripts/agent16_audit.py . --runtime --json-out reports/agent16_audit_report.json
python -m compileall ai_trading_brain backend scripts
python scripts/agent16_business_operating_mind.py . --out .agent16-business-os
pytest -q
```