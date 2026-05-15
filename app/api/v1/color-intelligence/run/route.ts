import { NextResponse } from "next/server";
import { runColorIntelligenceLocal } from "@/lib/color-intelligence/localRuntime";

const BACKEND_BASE = process.env.BACKEND_API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

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

export async function POST(request: Request) {
  const payload = await request.json();
  try {
    const response = await fetch(`${BACKEND_BASE}/api/v1/color-intelligence/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const text = await response.text();
    const body = parseBody(text);

    return NextResponse.json(body, { status: response.status });
  } catch {
    const local = runColorIntelligenceLocal(payload);
    return NextResponse.json(local, { status: 200 });
  }
}
