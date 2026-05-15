import { NextResponse } from "next/server";
import { runBeautyPerceptionGraphEngine } from "@/lib/beauty-perception-v29/beautyPerceptionGraphEngine";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runBeautyPerceptionGraphEngine(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
