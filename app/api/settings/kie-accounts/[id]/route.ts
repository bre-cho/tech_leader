import { NextResponse } from "next/server";
import { z } from "zod";
import { kieAccountStore } from "@/services/accounts/kieAccountStore";

const KieAccountUpdateSchema = z.object({
  label: z.string().optional(),
  apiKey: z.string().min(10).optional(),
  enabled: z.boolean().optional(),
});

export async function PATCH(req: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    const body = KieAccountUpdateSchema.parse(await req.json());
    const account = kieAccountStore.update({ ...body, id });
    return NextResponse.json(account);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}

export async function DELETE(_: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    return NextResponse.json(kieAccountStore.remove(id));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
