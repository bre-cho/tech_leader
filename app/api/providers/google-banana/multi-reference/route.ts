import { NextResponse } from "next/server";
import { bananaMultiReference } from "@/services/provider-google-banana/bananaMultiReference";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const result = await bananaMultiReference(body);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
