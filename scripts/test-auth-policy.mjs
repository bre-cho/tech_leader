import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const mainFile = path.join(repoRoot, 'backend/app/main.py');
const content = fs.readFileSync(mainFile, 'utf8');

const requiredMarkers = [
  'write_route_auth_guard',
  'enforce_write_route_auth',
  'WRITE_API_KEYS',
];

const missing = requiredMarkers.filter((marker) => !content.includes(marker));
if (missing.length) {
  console.error(`Auth policy check failed. Missing markers in backend/app/main.py: ${missing.join(', ')}`);
  process.exit(1);
}

console.log('Auth policy check passed.');
