import { NextResponse } from "next/server";
import { OpenRouterSettingsUpdateSchema } from "@/services/settings/openRouterTypes";
import { OpenRouterStore } from "@/services/settings/openRouterStore";

export async function GET() {
  return NextResponse.json(new OpenRouterStore().getPublic());
}

export async function PATCH(req: Request) {
  try {
    const body = OpenRouterSettingsUpdateSchema.parse(await req.json());
    return NextResponse.json(new OpenRouterStore().update(body));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
