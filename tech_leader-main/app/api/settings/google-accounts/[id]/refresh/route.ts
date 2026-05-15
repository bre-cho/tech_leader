import { NextResponse } from "next/server";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

export async function POST(_: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  try {
    const key = new GoogleAccountStore().getApiKey(id);
    const ok = key.length > 10;
    new GoogleAccountStore().markHealth(id, ok);
    return NextResponse.json({ id, status: ok ? "ok" : "failed" });
  } catch (error) {
    new GoogleAccountStore().markHealth(id, false);
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
