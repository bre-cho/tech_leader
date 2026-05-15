import { NextResponse } from "next/server";
import { generateVeo31WithManagedAccount } from "@/services/google-ai/veoRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(await generateVeo31WithManagedAccount(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
