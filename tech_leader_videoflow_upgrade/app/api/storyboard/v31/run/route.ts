import { NextResponse } from "next/server";
import { runStoryboardV31 } from "@/lib/storyboard-v31/storyboardV31Runtime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runStoryboardV31(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
