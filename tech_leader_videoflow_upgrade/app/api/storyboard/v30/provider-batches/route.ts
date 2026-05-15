import { NextResponse } from "next/server";
import { runStoryboardAgentV30 } from "@/lib/storyboard-v30/storyboardAgentRuntime";

export async function POST(req: Request) {
  try {
    const result = runStoryboardAgentV30(await req.json());
    return NextResponse.json({
      status: result.status,
      providerPayloads: result.providerPayloads,
      verification: result.verification,
      timeline: result.timeline
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
