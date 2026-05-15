from __future__ import annotations

from pathlib import Path
from .models import Finding

class PatchPlanner:
    def plan(self, findings: list[Finding]) -> list[Finding]:
        plans: list[Finding] = []
        for f in findings:
            if f.severity in {'P0','P1'}:
                plans.append(Finding(f.severity,'PHASE_5_PATCH_PLANNING','patch-plan',f.path,f"Patch required for {f.category}: {f.message}",self._recommend_patch(f),f.evidence))
        # de-duplicate
        seen=set(); uniq=[]
        for p in plans:
            key=(p.severity,p.path,p.message)
            if key not in seen:
                seen.add(key); uniq.append(p)
        return uniq

    def _recommend_patch(self, f: Finding) -> str:
        if f.category == 'syntax':
            return 'Mở file, sửa đúng line trong evidence, chạy python -m compileall.'
        if f.category == 'live-trading-safety':
            return 'Thêm RiskGuard.preflight(), idempotency_key, broker reconciliation và reject khi release_gate != GO.'
        if 'secret' in f.category:
            return 'Xóa secret khỏi repo, dùng ENV/secret manager, rotate key.'
        if f.category == 'runtime-validation':
            return 'Chạy command trong evidence, sửa lỗi đầu tiên theo stderr_tail.'
        return f.recommendation
