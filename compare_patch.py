import os
import hashlib
import subprocess

patch_root = "MVP_CREATIVE_OS_UIUX_FULL_PATCH"
mapping = {
    "backend/app": "backend/app",
    "frontend-next/app": "app",
    "frontend-next/components": "components",
    "frontend-next/types": "types",
    "frontend-vite/src": "frontend/src",
    "docs": "docs"
}

def get_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

results = []
summary = {"MISSING_TARGET": 0, "APPLIED_IDENTICAL": 0, "APPLIED_MODIFIED": 0}

for patch_subdir, target_subdir in mapping.items():
    patch_path = os.path.join(patch_root, patch_subdir)
    if not os.path.exists(patch_path):
        continue
    
    for root, dirs, files in os.walk(patch_path):
        for file in files:
            full_patch_file = os.path.join(root, file)
            rel_path = os.path.relpath(full_patch_file, patch_path)
            target_file = os.path.join(target_subdir, rel_path)
            
            status = ""
            diff = ""
            
            if not os.path.exists(target_file):
                status = "MISSING_TARGET"
            else:
                patch_hash = get_hash(full_patch_file)
                target_hash = get_hash(target_file)
                
                if patch_hash == target_hash:
                    status = "APPLIED_IDENTICAL"
                else:
                    status = "APPLIED_MODIFIED"
                    # Get diff
                    try:
                        diff_proc = subprocess.run(['diff', '-u', target_file, full_patch_file], capture_output=True, text=True)
                        diff = "\n".join(diff_proc.stdout.splitlines()[:15])
                    except:
                        diff = "Error getting diff"
            
            results.append({
                "patch_file": full_patch_file,
                "target_file": target_file,
                "status": status,
                "diff": diff,
                "is_doc": patch_subdir == "docs"
            })
            summary[status] += 1

print("--- FILE COMPARISON REPORT ---")
for r in results:
    print(f"Patch File: {r['patch_file']}")
    print(f"Target File: {r['target_file']}")
    print(f"Status: {r['status']}")
    if r['is_doc']:
        print(f"Doc Applied: {'Yes' if r['status'] != 'MISSING_TARGET' else 'No'}")
    if r['status'] == 'APPLIED_MODIFIED':
        print("Diff Context:")
        print(r['diff'])
    print("-" * 40)

print("\n--- SUMMARY ---")
for k, v in summary.items():
    print(f"{k}: {v}")
