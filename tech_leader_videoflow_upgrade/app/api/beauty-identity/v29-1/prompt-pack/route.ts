import { NextResponse } from "next/server";
import { runIdentityBeautyRuntime } from "@/lib/beauty-identity-v29/identityBeautyRuntime";

export async function POST(req: Request) {
  try {
    const result = runIdentityBeautyRuntime(await req.json());
    return NextResponse.json({
      status: result.status,
      providerRoute: result.providerRoute,
      promptPack: result.promptPack,
      providerPayloads: result.providerPayloads,
      qaReport: result.qaReport
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
