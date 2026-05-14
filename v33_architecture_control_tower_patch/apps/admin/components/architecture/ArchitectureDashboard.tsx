"use client";
import { useState } from "react";

export default function ArchitectureDashboard() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  async function callApi(url: string) {
    setLoading(true);
    const res = await fetch(url, { method: "POST" });
    setResult(await res.json());
    setLoading(false);
  }
  const decision = result?.promotion_decision ?? result?.decision;
  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">Architecture Control Tower</h1>
          <p className="mt-2 text-neutral-300">CodeGraph Snapshot → Blast Radius Diff → Architecture Drift Check → Promotion Gate.</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button onClick={() => callApi("/api/architecture/snapshot")} disabled={loading} className="rounded-2xl bg-white px-5 py-3 font-semibold text-black">Snapshot Before Patch</button>
            <button onClick={() => callApi("/api/architecture/compare")} disabled={loading} className="rounded-2xl bg-yellow-300 px-5 py-3 font-semibold text-black">Compare After Patch</button>
          </div>
        </div>
        {decision && <JsonPanel title="Promotion Gate" data={decision} />}
        {result?.blast_radius_report && <JsonPanel title="Blast Radius Report" data={result.blast_radius_report} />}
        {result?.drift_report && <JsonPanel title="Architecture Drift Report" data={result.drift_report} />}
        {result?.after_snapshot && <JsonPanel title="Architecture Map Summary" data={result.after_snapshot.summary} />}
        {result && <JsonPanel title="Raw Result" data={result} />}
      </section>
    </main>
  );
}
function JsonPanel({ title, data }: { title: string; data: any }) {
  return <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5"><h2 className="text-xl font-semibold">{title}</h2><pre className="mt-3 max-h-[520px] overflow-auto whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(data, null, 2)}</pre></div>;
}
