import { NextResponse } from "next/server";
import { z } from "zod";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

const RotationSchema = z.object({
  enabled: z.boolean(),
  strategy: z.enum(["round_robin", "least_recent", "weighted"]).default("round_robin"),
  perScene: z.boolean().default(true)
});

export async function POST(req: Request) {
  try {
    const rotation = RotationSchema.parse(await req.json());
    return NextResponse.json(new GoogleAccountStore().setRotation(rotation));
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
