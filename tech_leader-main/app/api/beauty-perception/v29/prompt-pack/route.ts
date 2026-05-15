import { NextResponse } from "next/server";
import { runBeautyPerceptionGraphEngine } from "@/lib/beauty-perception-v29/beautyPerceptionGraphEngine";

export async function POST(req: Request) {
  try {
    const result = runBeautyPerceptionGraphEngine(await req.json());
    return NextResponse.json({
      status: result.status,
      promptPack: result.promptPack,
      sceneSpec: result.sceneSpec,
      providerRoute: result.providerRoute,
      commercialBeautyScore: result.commercialBeautyScore
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
