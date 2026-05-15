import { NextResponse } from "next/server";
import { runStoryboardAgentV30SalesUpgraded } from "@/lib/storyboard-v30/storyboardAgentRuntime.sales-upgraded";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runStoryboardAgentV30SalesUpgraded(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
