import { NextResponse } from "next/server";
import { z } from "zod";
import { kieAccountStore } from "@/services/accounts/kieAccountStore";

const KieAccountCreateSchema = z.object({
  label: z.string().min(1),
  apiKey: z.string().min(10),
  enabled: z.boolean().default(true),
});

export async function GET() {
  return NextResponse.json(kieAccountStore.listPublic());
}

export async function POST(req: Request) {
  try {
    const body = KieAccountCreateSchema.parse(await req.json());
    const account = kieAccountStore.add(body);
    return NextResponse.json(account);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
