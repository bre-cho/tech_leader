import { NextResponse } from "next/server";
import { runBeautyCommerceEngine } from "@/services/beauty-commerce/beautyCommerceEngine";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const result = runBeautyCommerceEngine(body);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
