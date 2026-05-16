import os
import hashlib

mapping = [
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/backend/app/api/routes/creative_os.py", "backend/app/api/v1/creative_os.py"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/backend/app/creative_os/provider_duration_profiles.py", "backend/app/creative_os/provider_duration_profiles.py"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/backend/app/creative_os/safe_render_queue.py", "backend/app/creative_os/safe_render_queue.py"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/backend/app/creative_os/scene_count_planner.py", "backend/app/creative_os/scene_count_planner.py"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/backend/app/creative_os/schemas.py", "backend/app/creative_os/schemas.py"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/docs/README_PATCH.md", "docs/README_PATCH.md"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/docs/RENDER_SAFETY_RULES.md", "docs/RENDER_SAFETY_RULES.md"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-next/app/workflows/creative-os.css", "app/workflows/creative-os.css"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-next/app/workflows/page.tsx", "app/workflows/page.tsx"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-next/components/creative-os/CreativeOSControlPlane.tsx", "components/creative-os/CreativeOSControlPlane.tsx"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-next/types/creative-os.ts", "types/creative-os.ts"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-vite/src/creative-os/runtime/videoHandoffReceiver.ts", "frontend/src/creative-os/runtime/videoHandoffReceiver.ts"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-vite/src/pages/DesignStudioCreativeOS.tsx", "frontend/src/pages/DesignStudioCreativeOS.tsx"),
    ("MVP_CREATIVE_OS_UIUX_FULL_PATCH/frontend-vite/src/styles/creative-os.css", "frontend/src/styles/creative-os.css"),
]

def get_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

report_lines = ["# MVP Patch Compliance Report (14 Files)", ""]
report_lines.append("| Source | Target | Status | Result |")
report_lines.append("| :--- | :--- | :--- | :--- |")

stats = {"MISSING_TARGET": 0, "APPLIED_IDENTICAL": 0, "APPLIED_MODIFIED": 0}
results = {"PASS": 0, "FAIL": 0}

for src, tgt in mapping:
    status = ""
    result = ""
    if not os.path.exists(tgt):
        status = "MISSING_TARGET"
        result = "FAIL"
    else:
        src_hash = get_hash(src)
        tgt_hash = get_hash(tgt)
        if src_hash == tgt_hash:
            status = "APPLIED_IDENTICAL"
        else:
            status = "APPLIED_MODIFIED"
        result = "PASS"
    
    stats[status] += 1
    results[result] += 1
    report_lines.append(f"| {src} | {tgt} | {status} | {result} |")

report_lines.append("")
report_lines.append("## Summary")
for k, v in stats.items():
    report_lines.append(f"- {k}: {v}")
for k, v in results.items():
    report_lines.append(f"- {k}: {v}")

with open("reports/mvp_patch_compliance_14files.md", "w") as f:
    f.write("\n".join(report_lines))

print("Summary Counts:")
for k, v in stats.items(): print(f"{k}: {v}")
for k, v in results.items(): print(f"{k}: {v}")
print("\nFirst 30 lines of report:")
print("\n".join(report_lines[:30]))
