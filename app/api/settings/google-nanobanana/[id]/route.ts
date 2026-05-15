import { NextResponse } from "next/server";
import { z } from "zod";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

const NanoBananaUpdateSchema = z.object({
  label: z.string().min(1).optional(),
  apiKey: z.string().min(10).optional(),
  enabled: z.boolean().optional(),
  quotaWeight: z.number().min(1).max(100).optional(),
});

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

export async function PATCH(req: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    ensureNanoAccount(id);
    const body = NanoBananaUpdateSchema.parse(await req.json());
    const account = new GoogleAccountStore().update({
      id,
      ...body,
      capabilities: ["nano_banana"],
    });
    return NextResponse.json(account);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }
}

export async function DELETE(_: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    ensureNanoAccount(id);
    return NextResponse.json(new GoogleAccountStore().remove(id));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }
}
