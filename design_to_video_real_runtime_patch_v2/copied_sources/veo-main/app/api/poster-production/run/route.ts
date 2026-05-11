import { NextResponse } from "next/server";
import { z } from "zod";

import { runPosterProductionPipeline } from "@/lib/poster-production/orchestrator";
import { getUserFromBearer } from "@/lib/supabase/server";
import { observability } from "@/lib/observability";
import { enforceDistributedRateLimit } from "@/lib/rate-limit/distributed";
import { parseEnvNumber } from "@/lib/env-utils";
import { ensureObservabilityExporterStarted } from "@/lib/observability/exporter";

const PosterProductionInputSchema = z
  .object({
    text: z.string().optional(),
    product: z.string().optional(),
    product_type: z.string().optional(),
    brand: z.string().optional(),
    industry: z.string().optional(),
    audience: z.string().optional(),
    goal: z.enum(["sale", "lead", "click", "education", "event", "conversion"]).optional(),
    platform: z.string().optional(),
    ratio: z.string().optional(),
    perception_targets: z.array(z.string()).optional(),
    headline: z.string().optional(),
    cta: z.string().optional(),
    value_icons: z.array(z.string()).optional(),
    hasPackaging: z.boolean().optional(),
    hasCollection: z.boolean().optional(),
    useReferenceImage: z.boolean().optional(),
  })
  .refine((value) => Boolean(value.text || value.product || value.product_type), {
    message: "Missing text, product, or product_type",
  });

export async function POST(req: Request) {
  try {
    ensureObservabilityExporterStarted();
    const auth = await getUserFromBearer(req);
    if (!auth.user) {
      observability.recordAuthFailure("/api/poster-production/run", 401);
      return NextResponse.json({ error: auth.error }, { status: 401 });
    }
    const rate = await enforceDistributedRateLimit({
      bucket: "api/poster-production/run",
      key: auth.user.id,
      max: parseEnvNumber("RATE_LIMIT_POSTER_PRODUCTION_RUN_PER_MINUTE", 6, (n) => n > 0),
      windowSec: 60,
    });
    if (!rate.allowed) {
      return NextResponse.json(
        { error: "Too many requests for poster production. Please retry later." },
        {
          status: 429,
          headers: {
            "retry-after": String(rate.retryAfterSec || 60),
            "x-ratelimit-limit": String(rate.limit),
            "x-ratelimit-remaining": String(rate.remaining),
          },
        }
      );
    }

    const payload = PosterProductionInputSchema.parse(await req.json());
    const result = await runPosterProductionPipeline(payload);
    return NextResponse.json(result);
  } catch (error: unknown) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid payload", details: error.issues },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Poster production failed" },
      { status: 500 }
    );
  }
}
