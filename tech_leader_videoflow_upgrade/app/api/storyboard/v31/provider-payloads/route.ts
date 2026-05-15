import { NextResponse } from "next/server";
import { runStoryboardV31 } from "@/lib/storyboard-v31/storyboardV31Runtime";

export async function POST(req: Request) {
  try {
    const result = runStoryboardV31(await req.json());
    return NextResponse.json({
      status: result.status,
      providerPayloads: result.providerPayloads,
      rhythmGraph: result.rhythmGraph,
      verification: result.verification
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
