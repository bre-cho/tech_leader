import { NextResponse } from "next/server";
import { generateNanoBananaWithManagedAccount } from "@/services/google-ai/nanoBananaRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(await generateNanoBananaWithManagedAccount(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
