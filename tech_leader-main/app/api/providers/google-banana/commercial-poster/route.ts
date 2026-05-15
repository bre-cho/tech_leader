import { NextResponse } from "next/server";
import { bananaImageGenerate } from "@/services/provider-google-banana/bananaImageGenerate";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const result = await bananaImageGenerate({ ...body, mode: 'commercial_poster' });
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
