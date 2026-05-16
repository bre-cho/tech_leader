"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function BlendRetouchStudio() {
  const [file, setFile] = useState<File | null>(null);
  const [preset, setPreset] = useState("beauty_clean");
  const [useCase, setUseCase] = useState("beauty");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!file) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("brand_name", "Demo Brand");
      form.append("use_case", useCase);
      form.append("preset", preset);
      form.append("strength", "0.65");
      form.append("skin_protection", "true");
      form.append("texture_preservation", "true");
      form.append("export_scale", "preview");

      const res = await fetch(`${API_BASE}/api/v1/blend-retouch/run`, { method: "POST", body: form });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-6xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V24 - AI Blend and Retouch Engine</h1>
          <p className="mt-2 text-neutral-300">Perception-aware visual finishing, not a filter stack.</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <select value={preset} onChange={(e) => setPreset(e.target.value)} className="rounded-xl bg-neutral-800 px-3 py-2">
              {[
                "korean_tone",
                "japanese_soft",
                "film_tone",
                "vintage",
                "wedding_studio",
                "fashion_editorial",
                "beauty_clean",
              ].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <select value={useCase} onChange={(e) => setUseCase(e.target.value)} className="rounded-xl bg-neutral-800 px-3 py-2">
              {["wedding", "studio", "fashion", "beauty", "lookbook", "product"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <button onClick={run} disabled={loading} className="btn-primary">
              {loading ? "Running..." : "Run Blend and Retouch"}
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
