import { NextResponse } from "next/server";
import { runIdentityBeautyRuntime } from "@/lib/beauty-identity-v29/identityBeautyRuntime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runIdentityBeautyRuntime(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
