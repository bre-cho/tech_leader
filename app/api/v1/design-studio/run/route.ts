import { NextResponse } from "next/server";
import { runDesignStudioLocalFallback } from "@/lib/design/localFallback";
import type { DesignStudioRequest } from "@/lib/design/pipeline-api";

const BACKEND_BASE = process.env.BACKEND_API_BASE || process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type BackendDesignPayload = {
  industry: string;
  product: string;
  audience: string;
  channel: string;
  goal: string;
  brand_name: string;
  tone: string;
  budget_tier: "low" | "mid" | "premium";
  language: string;
  dry_run: boolean;
};

function parseBody(text: string): unknown {
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

function toBackendPayload(payload: DesignStudioRequest): BackendDesignPayload {
  return {
    industry: payload.industry,
    product: payload.product,
    audience: payload.audience,
    channel: payload.channel,
    goal: payload.goal,
    brand_name: payload.brand_name,
    tone: payload.tone,
    budget_tier: payload.budget_tier,
    language: payload.language,
    dry_run: payload.dry_run,
  };
}

export async function POST(request: Request) {
  const payload = (await request.json()) as DesignStudioRequest;

  try {
    const response = await fetch(`${BACKEND_BASE}/api/v1/design-studio/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toBackendPayload(payload)),
      cache: "no-store",
    });

    const text = await response.text();
    const body = parseBody(text);
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json(runDesignStudioLocalFallback(payload), { status: 200 });
  }
}
