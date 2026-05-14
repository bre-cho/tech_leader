import { NextResponse } from "next/server";
import { runFacialAestheticEngine } from "@/lib/facial-aesthetic-v28-1/facialAestheticEngine";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    return NextResponse.json(runFacialAestheticEngine(body));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
