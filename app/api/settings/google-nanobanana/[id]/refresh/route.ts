import { NextResponse } from "next/server";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

function ensureNanoAccount(id: string) {
  const state = new GoogleAccountStore().listPublic();
  const account = state.accounts.find((item) => item.id === id);
  if (!account) {
    throw new Error("Google account not found.");
  }
  if (!account.capabilities.includes("nano_banana")) {
    throw new Error("Account does not support nano_banana.");
  }
}

export async function POST(_: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  try {
    ensureNanoAccount(id);
    const key = new GoogleAccountStore().getApiKey(id);
    const ok = key.length > 10;
    new GoogleAccountStore().markHealth(id, ok);
    return NextResponse.json({ id, status: ok ? "ok" : "failed" });
  } catch (error) {
    new GoogleAccountStore().markHealth(id, false);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }
}
