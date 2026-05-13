import { NextRequest, NextResponse } from "next/server";
import { AutoVideoFromPoster, PosterToVideoRequestSchema } from "@/lib/poster-intelligence";
import { isProductionLikeRuntime } from "@/lib/config/runtime-guards";
import { log } from "@/lib/logger";

export async function POST(req: NextRequest) {
  try {
    const payload = await req.json();
    const validated = PosterToVideoRequestSchema.parse(payload);

    if (validated.provider === "mock" && isProductionLikeRuntime()) {
      log(
        "error",
        "api/poster-intelligence/poster-to-video",
        "Video provider is 'mock' in a production-like environment. " +
          "Set provider to 'veo', 'runway', or 'pika' for real rendering.",
        { provider: validated.provider }
      );
      return NextResponse.json(
        {
          error:
            "Service unavailable: video provider is 'mock' in a production-like environment. " +
            "Set provider to 'veo', 'runway', or 'pika'.",
        },
        { status: 503 }
      );
    }

    const result = new AutoVideoFromPoster().build(validated);
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof Error) {
      return NextResponse.json({ error: error.message }, { status: 400 });
    }
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
