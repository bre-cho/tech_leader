import { NextResponse } from "next/server";
import { openRouterChat } from "@/services/settings/openRouterClient";

export async function POST() {
  try {
    const result = await openRouterChat([{ role: "user", content: "Reply with OK." }]);
    return NextResponse.json({ status: "ok", result });
  } catch (error) {
    return NextResponse.json({ status: "failed", error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
