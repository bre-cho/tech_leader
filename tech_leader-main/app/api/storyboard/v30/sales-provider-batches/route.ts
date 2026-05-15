import { NextResponse } from "next/server";
import { runStoryboardAgentV30SalesUpgraded } from "@/lib/storyboard-v30/storyboardAgentRuntime.sales-upgraded";

export async function POST(req: Request) {
  try {
    const result = runStoryboardAgentV30SalesUpgraded(await req.json());
    return NextResponse.json({
      status: result.status,
      salesEngineV3: result.salesEngineV3,
      providerPayloads: result.providerPayloads,
      verification: result.verification,
      timeline: result.timeline
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
