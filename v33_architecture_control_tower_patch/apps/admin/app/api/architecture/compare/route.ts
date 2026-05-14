import { NextResponse } from "next/server";
import { execFileSync } from "node:child_process";
import fs from "node:fs";

export async function POST() {
  try {
    execFileSync("architecture-observer", ["compare", "--before", "runtime/architecture-governance/snapshot_before.json", "--repo", ".", "--out-dir", "runtime/architecture-governance"], { stdio: "pipe" });
  } catch (_error) {}
  const read = (p: string) => fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
  return NextResponse.json({
    status: "ready",
    after_snapshot: read("runtime/architecture-governance/snapshot_after.json"),
    blast_radius_report: read("runtime/architecture-governance/blast_radius_report.json"),
    drift_report: read("runtime/architecture-governance/drift_report.json"),
    promotion_decision: read("runtime/architecture-governance/promotion_decision.json")
  });
}
