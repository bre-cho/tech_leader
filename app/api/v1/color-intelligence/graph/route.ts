import { NextResponse } from "next/server";
import { getColorGraphLocal } from "@/lib/color-intelligence/localRuntime";

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

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/v1/color-intelligence/graph`, {
      method: "GET",
      cache: "no-store",
    });

    const text = await response.text();
    const body = parseBody(text);

    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json(getColorGraphLocal(), { status: 200 });
  }
}
