import { NextRequest, NextResponse } from "next/server";
import { enhancePromptWithFaceWidthLock, scoreFaceBalancePrompt } from "@/lib/beauty-intelligence/face-balance";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    if (body.mode === "score") {
      return NextResponse.json({
        ok: true,
        score: scoreFaceBalancePrompt(body.prompt || "", body.negativePrompt || "")
      });
    }

    if (!body.basePrompt && !body.prompt) {
      return NextResponse.json({ ok: false, error: "basePrompt hoặc prompt là bắt buộc" }, { status: 400 });
    }

    const result = enhancePromptWithFaceWidthLock({
      basePrompt: body.basePrompt || body.prompt,
      negativePrompt: body.negativePrompt,
      provider: body.provider || "generic",
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
