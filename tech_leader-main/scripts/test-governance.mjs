import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const files = [
  'backend/app/governance/operating_law.py',
  'backend/app/runtime/orchestrator.py',
  'backend/app/runtime/verification.py',
  'backend/app/workforce/orchestrator.py',
];

const requiredSteps = [
  'target_define',
  'research',
  'plan',
  'execute',
  'verify',
  'distill_to_skill',
  'memory_update',
  'winner_dna_update',
];

const violations = [];
for (const rel of files) {
  const content = fs.readFileSync(path.join(repoRoot, rel), 'utf8');
  for (const step of requiredSteps) {
    if (!content.includes(step)) {
      violations.push(`${rel} missing lifecycle marker: ${step}`);
    }
  }
}

if (violations.length) {
  console.error('Governance check failed:\n' + violations.join('\n'));
  process.exit(1);
}
console.log('Governance check passed.');
