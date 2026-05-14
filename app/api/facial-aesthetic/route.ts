import { analyzeFacialAesthetic } from "@/lib/facial-aesthetic";

export async function POST(req: Request): Promise<Response> {
  try {
    const body = await req.json();
    const result = analyzeFacialAesthetic(body);
    return Response.json(result, { status: result.ok ? 200 : 422 });
  } catch (error) {
    return Response.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "Unknown facial aesthetic engine error"
      },
      { status: 400 }
    );
  }
}
