import { NextResponse } from "next/server";
import { runStoryboardAgentV30 } from "@/lib/storyboard-v30/storyboardAgentRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runStoryboardAgentV30(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
