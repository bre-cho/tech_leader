#!/usr/bin/env node
/**
 * check-release-gate.mjs
 *
 * Calls GET /api/v1/audit/release-gate on the running backend.
 * Exits 0 (GO) or 1 (NO-GO / unreachable).
 *
 * Usage:
 *   node scripts/check-release-gate.mjs [--api-base http://localhost:8000]
 */
import { parseArgs } from "node:util";

const { values } = parseArgs({
  args: process.argv.slice(2),
  options: { "api-base": { type: "string", default: "http://localhost:8000" } },
});

const apiBase = values["api-base"];
const url = `${apiBase}/api/v1/audit/release-gate`;

console.log(`[release-gate] Checking ${url} ...`);

let body;
try {
  const resp = await fetch(url);
  if (!resp.ok) {
    console.error(`[release-gate] HTTP ${resp.status} from ${url}`);
    process.exit(1);
  }
  body = await resp.json();
} catch (err) {
  console.error(`[release-gate] Could not reach backend: ${err.message}`);
  console.error("[release-gate] Make sure the backend is running (uvicorn app.main:app --port 8000)");
  process.exit(1);
}

const { status, reason, blocking_failures, overall_health_score } = body;

console.log(`[release-gate] Status: ${status}`);
console.log(`[release-gate] Health score: ${overall_health_score ?? "n/a"}`);
console.log(`[release-gate] Reason: ${reason}`);

if (blocking_failures?.length) {
  console.error("[release-gate] Blocking failures:");
  for (const f of blocking_failures) {
    console.error(`  - ${f}`);
  }
}

if (status !== "GO") {
  console.error(`[release-gate] ❌ NO-GO — cannot proceed to release.`);
  process.exit(1);
}

console.log("[release-gate] ✅ GO — release gate passed.");
process.exit(0);
