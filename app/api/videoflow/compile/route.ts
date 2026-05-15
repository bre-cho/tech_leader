import { NextResponse } from "next/server";
import { runStoryboardV31 } from "@/lib/storyboard-v31/storyboardV31Runtime";
import { compileStoryboardToVideoFlow, verifyVideoFlowTimeline } from "@/lib/videoflow";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const storyboard = runStoryboardV31(body);
    const videoFlowTimeline = compileStoryboardToVideoFlow(storyboard);
    const verification = verifyVideoFlowTimeline(videoFlowTimeline);

    return NextResponse.json({
      status: verification.passed ? "ready" : "blocked",
      storyboardStatus: storyboard.status,
      videoFlowTimeline,
      verification,
      artifacts: storyboard.artifacts
    });
  } catch (error) {
    return NextResponse.json(
      { status: "error", error: error instanceof Error ? error.message : "Unknown VideoFlow compile error" },
      { status: 400 }
    );
  }
}
