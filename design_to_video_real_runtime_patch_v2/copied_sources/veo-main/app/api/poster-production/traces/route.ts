import { NextResponse } from "next/server";

import { listPosterProductionTraces } from "@/lib/poster-production/traces";
import { getUserFromBearer } from "@/lib/supabase/server";
import { observability } from "@/lib/observability";

export async function GET(req: Request) {
  const auth = await getUserFromBearer(req);
  if (!auth.user) {
    observability.recordAuthFailure("/api/poster-production/traces", 401);
    return NextResponse.json({ error: auth.error || "Unauthorized" }, { status: 401 });
  }
  const { searchParams } = new URL(req.url);
  const limit = Math.min(Number(searchParams.get("limit") || "20"), 100);
  const traces = await listPosterProductionTraces(limit);

  return NextResponse.json({ traces, count: traces.length });
}
