import { NextResponse } from "next/server";
import { BeautyCommerceInputSchema } from "@/lib/beauty-commerce-v28/types";
import { buildBananaMultiReferenceEngine } from "@/lib/beauty-commerce-v28/bananaMultiReferenceEngine";

export async function POST(req: Request) {
  try {
    const input = BeautyCommerceInputSchema.parse(await req.json());
    return NextResponse.json(buildBananaMultiReferenceEngine(input));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
