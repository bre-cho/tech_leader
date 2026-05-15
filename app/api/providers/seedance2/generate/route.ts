import { NextResponse } from "next/server";
import { generateSeedance2Video } from "@/services/seedance2/seedance2Runtime";

export async function POST(req: Request) {
  try {
    return NextResponse.json(await generateSeedance2Video(await req.json()));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
