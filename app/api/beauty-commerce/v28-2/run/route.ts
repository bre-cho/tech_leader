import { NextResponse } from "next/server";
import { runBeautyCommerceV28 } from "@/lib/beauty-commerce-v28/beautyCommerceV28Engine";

export async function POST(req: Request) {
  try {
    return NextResponse.json(runBeautyCommerceV28(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
