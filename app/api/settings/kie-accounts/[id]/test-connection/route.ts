/**
 * POST /api/settings/kie-accounts/[id]/test-connection
 *
 * Security model:
 *   - The KIE API key lives ONLY in backend/.env (SEEDANCE_API_KEY).
 *   - This Next.js route proxies the test request to the backend.
 *   - The backend calls kie.ai and returns ok/fail.
 *   - The key is never sent to or stored in the Next.js process.
 */
import { NextResponse } from "next/server";

const BACKEND_API = process.env.BACKEND_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function POST(_: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  try {
    const res = await fetch(`${BACKEND_API}/seedance/test-connection`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ account_id: id }),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.ok ? 200 : res.status });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: err instanceof Error ? err.message : "Backend unreachable" },
      { status: 200 }
    );
  }
}
