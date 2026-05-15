import { NextResponse } from "next/server";
import { generateRunwayVideo } from "@/services/runway/runwayRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(await generateRunwayVideo(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
