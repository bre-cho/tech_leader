import { NextResponse } from "next/server";
import { execFileSync } from "node:child_process";
import fs from "node:fs";

export async function POST() {
  try {
    execFileSync("architecture-observer", ["snapshot", "--repo", ".", "--out", "runtime/architecture-governance/snapshot_before.json"], { stdio: "pipe" });
    const data = JSON.parse(fs.readFileSync("runtime/architecture-governance/snapshot_before.json", "utf8"));
    return NextResponse.json({ status: "ready", snapshot: data });
  } catch (error) {
    return NextResponse.json({ status: "failed", error: error instanceof Error ? error.message : String(error) }, { status: 500 });
  }
}
