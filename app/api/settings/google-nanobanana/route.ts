import { NextResponse } from "next/server";
import { z } from "zod";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

const NanoBananaCreateSchema = z.object({
  label: z.string().min(1),
  apiKey: z.string().min(10),
  enabled: z.boolean().default(true),
  quotaWeight: z.number().min(1).max(100).default(1),
});

export async function GET() {
  const state = new GoogleAccountStore().listPublic();
  return NextResponse.json({
    accounts: state.accounts.filter((account) => account.capabilities.includes("nano_banana")),
    rotation: state.rotation,
  });
}

export async function POST(req: Request) {
  try {
    const body = NanoBananaCreateSchema.parse(await req.json());
    const account = new GoogleAccountStore().add({
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
