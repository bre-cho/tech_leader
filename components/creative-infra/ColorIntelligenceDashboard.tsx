"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ColorIntelligenceDashboard() {
  const [result, setResult] = useState<any>(null);
  const [graph, setGraph] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run(useCase = "showroom", industry = "spa") {
    setLoading(true);
    try {
      const payload = {
        brand_name: industry === "spa" ? "Serene Spa" : "Demo Brand",
        industry,
        use_case: useCase,
        audience: "premium buyers in Vietnam / Asia",
        desired_perception: ["trust", "luxury", "warmth", "conversion"],
        cultural_context: "Vietnam / Asia",
      };
      const runRes = await fetch(`${API_BASE}/api/v1/color-intelligence/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const runJson = await runRes.json();
      setResult(runJson);

      const graphRes = await fetch(`${API_BASE}/api/v1/color-intelligence/graph`);
      setGraph(await graphRes.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-6xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V23 - Color Intelligence Graph</h1>
          <p className="mt-2 text-neutral-300">COLOR != VISUAL. COLOR = PERCEPTION SYSTEM.</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button onClick={() => run("showroom", "spa")} disabled={loading} className="rounded-xl bg-white px-4 py-2 font-semibold text-black">Spa Showroom</button>
            <button onClick={() => run("showroom", "luxury fashion")} disabled={loading} className="rounded-xl border border-neutral-600 px-4 py-2">Luxury Fashion</button>
            <button onClick={() => run("restore_photo", "restore photo")} disabled={loading} className="rounded-xl border border-neutral-600 px-4 py-2">Restore Photo</button>
          </div>
        </div>

        {result && (
          <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
            <h2 className="text-xl font-semibold">Palette</h2>
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {result.palette?.map((c: any) => (
                <div key={c.name} className="overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-950">
                  <div className="h-20" style={{ backgroundColor: c.hex }} />
                  <div className="p-3">
                    <div className="font-semibold">{c.name}</div>
                    <div className="text-sm text-neutral-400">{c.role}</div>
                    <div className="mt-1 text-xs text-neutral-500">{(c.perception || []).join(", ")}</div>
                  </div>
                </div>
              ))}
            </div>
            <pre className="mt-4 overflow-auto rounded-2xl bg-neutral-950 p-4 text-xs text-neutral-300">{JSON.stringify({ scores: result.perception_scores, material: result.material_plan, lighting: result.lighting_plan }, null, 2)}</pre>
          </div>
        )}

        {graph && (
          <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
            <h2 className="text-xl font-semibold">Graph Edges</h2>
            <div className="mt-3 grid gap-2">
              {(graph.items || []).slice(-12).map((e: any, i: number) => (
                <div key={`${e.source}-${i}`} className="rounded-xl border border-neutral-800 bg-neutral-950 p-3 text-sm text-neutral-300">
                  {e.source} -> {e.relation} -> {e.target} ({e.weight})
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
