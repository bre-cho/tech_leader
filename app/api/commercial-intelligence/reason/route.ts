import { NextResponse } from "next/server";

const BACKEND_API_BASE = process.env.BACKEND_API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export async function POST(req: Request) {
  try {
    const payload = await req.json();
    const response = await fetch(`${BACKEND_API_BASE}/api/v1/commercial-intelligence/reason`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json") ? await response.json() : { error: await response.text() };
    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to reach backend API" },
      { status: 502 },
    );
  }
}