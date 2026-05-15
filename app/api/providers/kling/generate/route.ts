import { NextResponse } from "next/server";
import { generateKlingVideo } from "@/services/kling/klingRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(await generateKlingVideo(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
