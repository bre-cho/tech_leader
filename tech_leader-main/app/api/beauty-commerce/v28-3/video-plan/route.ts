import { NextResponse } from "next/server";
import { runBeautyCommerceV28 } from "@/lib/beauty-commerce-v28/beautyCommerceV28Engine";

export async function POST(req: Request) {
  try {
    const result = runBeautyCommerceV28(await req.json());
    return NextResponse.json({
      videoPlan: result.videoPlan,
      providerPayloads: result.providerPayloads,
      verification: result.verification,
      commercialScore: result.commercialScore
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
