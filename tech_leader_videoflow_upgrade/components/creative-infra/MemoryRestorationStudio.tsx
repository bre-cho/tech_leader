"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function MemoryRestorationStudio() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState("restore_colorize_8k");
  const [preset, setPreset] = useState("family_memory");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!file) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("customer_key", "demo_customer");
      form.append("mode", mode);
      form.append("preset", preset);
      form.append("strength", "0.65");
      form.append("face_restore", "true");
      form.append("colorize", mode !== "restore_only" && mode !== "keep_bw" ? "true" : "false");
      form.append("natural_asian_skin_tones", "true");
      form.append("print_export", "true");
      form.append("export_scale", "preview");

      const res = await fetch(`${API_BASE}/api/v1/memory-restoration/run`, { method: "POST", body: form });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-6xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V25 - AI Memory Restoration Engine</h1>
          <p className="mt-2 text-neutral-300">Restore first, recolor second, upscale last.</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <select value={mode} onChange={(e) => setMode(e.target.value)} className="rounded-xl bg-neutral-800 px-3 py-2">
              {["restore_only", "restore_colorize", "restore_colorize_8k", "keep_bw"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <select value={preset} onChange={(e) => setPreset(e.target.value)} className="rounded-xl bg-neutral-800 px-3 py-2">
              {["portrait", "family_memory", "wedding_archive", "memorial", "historical"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <button onClick={run} disabled={loading} className="rounded-xl bg-white px-4 py-2 font-semibold text-black">
              {loading ? "Running..." : "Run Restoration"}
            </button>
          </div>
        </div>

        {result && (
          <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
            <h2 className="text-xl font-semibold">Result</h2>
            <pre className="mt-3 overflow-auto rounded-2xl bg-neutral-950 p-4 text-xs text-neutral-300">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </section>
    </main>
  );
}
