import { NextResponse } from "next/server";
import { bananaImageEdit } from "@/services/provider-google-banana/bananaImageEdit";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const result = await bananaImageEdit({ ...body, mode: 'upscale_8k' });
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
