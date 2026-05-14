"use client";

import { useState } from "react";

type Provider = "sdxl" | "flux" | "hidream" | "veo" | "runway" | "kling" | "generic";

export function FaceBalancePanel() {
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [provider, setProvider] = useState<Provider>("flux");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function enhance() {
    setLoading(true);
    try {
      const res = await fetch("/api/beauty/face-balance/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ basePrompt: prompt, negativePrompt, provider, strictGate: true })
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  const score = result?.score;

  return (
    <section className="rounded-2xl border bg-white p-5 shadow-sm space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Face Width Lock — Fix cằm nhọn</h2>
        <p className="text-sm text-gray-600">
          Giữ chiều rộng phần cằm, giảm V-line AI, tăng soft U-shape real K-beauty face.
        </p>
      </div>

      <select className="w-full rounded-xl border p-2" value={provider} onChange={(e) => setProvider(e.target.value as Provider)}>
        {["flux", "hidream", "sdxl", "veo", "runway", "kling", "generic"].map((p) => <option key={p} value={p}>{p}</option>)}
      </select>

      <textarea className="min-h-36 w-full rounded-xl border p-3 text-sm" placeholder="Dán prompt gốc..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <textarea className="min-h-24 w-full rounded-xl border p-3 text-sm" placeholder="Negative prompt gốc..." value={negativePrompt} onChange={(e) => setNegativePrompt(e.target.value)} />

      <button onClick={enhance} disabled={loading || !prompt.trim()} className="rounded-xl bg-black px-4 py-2 text-white disabled:opacity-50">
        {loading ? "Đang fix..." : "Fix cằm nhọn"}
      </button>

      {score && (
        <div className="rounded-xl bg-gray-50 p-3 text-sm">
          <div className="font-semibold">Face balance score: {score.total}/100 — {score.grade}</div>
          <div className="mt-2 grid grid-cols-2 gap-2">
            <div>U-shape: {score.uShapeStructure}</div>
            <div>Chin base width: {score.chinBaseWidth}</div>
            <div>Jaw width: {score.jawWidthRetention}</div>
            <div>Cheek fullness: {score.cheekFullness}</div>
            <div>Anti V-line: {score.antiVLine}</div>
          </div>
        </div>
      )}

      {result?.prompt && (
        <div className="space-y-2">
          <label className="font-semibold text-sm">Prompt đã fix cằm</label>
          <textarea readOnly className="min-h-40 w-full rounded-xl border p-3 text-sm" value={result.prompt} />
          <label className="font-semibold text-sm">Negative prompt</label>
          <textarea readOnly className="min-h-28 w-full rounded-xl border p-3 text-sm" value={result.negativePrompt} />
        </div>
      )}
    </section>
  );
}
