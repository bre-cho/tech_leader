import { NextRequest, NextResponse } from "next/server";
import { enhanceScenePromptWithHairRealism, scoreHairRealismPrompt } from "@/lib/beauty-intelligence/hair-realism";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    if (body.mode === "score") {
      const score = scoreHairRealismPrompt(body.prompt || "", body.negativePrompt || "");
      return NextResponse.json({ ok: true, score });
    }

    if (!body.basePrompt && !body.prompt) {
      return NextResponse.json(
        { ok: false, error: "basePrompt hoặc prompt là bắt buộc" },
        { status: 400 }
      );
    }

    const result = enhanceScenePromptWithHairRealism({
      sceneId: body.sceneId,
      basePrompt: body.basePrompt || body.prompt,
      negativePrompt: body.negativePrompt,
      provider: body.provider || "generic",
      sceneType: body.sceneType,
      camera: body.camera,
      lighting: body.lighting,
      strictGate: Boolean(body.strictGate)
    });

    return NextResponse.json({ ok: true, ...result });
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
