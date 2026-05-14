import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const files = [
  'backend/app/config.py',
  'backend/app/runtime/verification.py',
  'backend/app/runtime/orchestrator.py',
  'backend/app/api/routes.py',
  'backend/app/api/workforce_routes.py',
];

const blockedPatterns = [
  /"mock_artifact"/,
  /"mock_checksum"/,
  /provider:\s*str\s*=\s*"mock"/,
  /hidream_provider:\s*str\s*=.*"mock"/,
];

const violations = [];
for (const rel of files) {
  const file = path.join(repoRoot, rel);
  const content = fs.readFileSync(file, 'utf8');
  for (const pattern of blockedPatterns) {
    if (pattern.test(content)) {
      violations.push(`${rel} matches ${pattern}`);
    }
  }
}

if (violations.length) {
  console.error('Mock leakage check failed:\n' + violations.join('\n'));
  process.exit(1);
}
console.log('Mock leakage check passed.');
