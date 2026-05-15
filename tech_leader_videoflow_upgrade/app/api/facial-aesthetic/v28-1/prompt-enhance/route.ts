import { NextResponse } from "next/server";
import { runFacialAestheticEngine } from "@/lib/facial-aesthetic-v28-1/facialAestheticEngine";

export async function POST(req: Request) {
  try {
    const result = runFacialAestheticEngine(await req.json());
    return NextResponse.json({
      prompt_enhancer: result.prompt_enhancer,
      negative_prompt: result.negative_prompt,
      face_dna: result.face_dna,
      scoring: result.luxury_face_scoring
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
