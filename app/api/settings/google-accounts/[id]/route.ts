import { NextResponse } from "next/server";
import { GoogleAccountUpdateSchema } from "@/services/accounts/accountTypes";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

export async function PATCH(req: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    const body = await req.json();
    const account = new GoogleAccountStore().update(GoogleAccountUpdateSchema.parse({ ...body, id }));
    return NextResponse.json(account);
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}

export async function DELETE(_: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    return NextResponse.json(new GoogleAccountStore().remove(id));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
