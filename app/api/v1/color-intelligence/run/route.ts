import { NextResponse } from "next/server";

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
  try {
    const payload = await request.json();
    const response = await fetch(`${BACKEND_BASE}/api/v1/color-intelligence/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const text = await response.text();
    const body = parseBody(text);

    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Cannot reach backend color-intelligence run endpoint.",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 502 },
    );
  }
}
