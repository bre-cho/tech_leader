"use client";

import { useState } from "react";

type Provider = "sdxl" | "flux" | "hidream" | "veo" | "runway" | "kling" | "generic";

export function HairRealismPanel() {
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [sceneId, setSceneId] = useState(1);
  const [provider, setProvider] = useState<Provider>("flux");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function enhance() {
    setLoading(true);
    try {
      const res = await fetch("/api/beauty/hair-realism/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sceneId, provider, basePrompt: prompt, negativePrompt, strictGate: true })
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
        <h2 className="text-xl font-semibold">Hair Realism Engine V2</h2>
        <p className="text-sm text-gray-600">
          Tối ưu tóc thật cho người mẫu ảo KOL: từng sợi tóc rõ nét, tóc con tự nhiên, ánh sáng tóc vật lý.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm">
          Scene ID
          <input
            className="mt-1 w-full rounded-xl border p-2"
            type="number"
            min={1}
            max={160}
            value={sceneId}
            onChange={(e) => setSceneId(Number(e.target.value))}
          />
        </label>

        <label className="text-sm">
          Provider
          <select
            className="mt-1 w-full rounded-xl border p-2"
            value={provider}
            onChange={(e) => setProvider(e.target.value as Provider)}
          >
            {["flux", "hidream", "sdxl", "veo", "runway", "kling", "generic"].map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </label>
      </div>

      <textarea
        className="min-h-32 w-full rounded-xl border p-3 text-sm"
        placeholder="Dán prompt scene gốc..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <textarea
        className="min-h-20 w-full rounded-xl border p-3 text-sm"
        placeholder="Negative prompt gốc..."
        value={negativePrompt}
        onChange={(e) => setNegativePrompt(e.target.value)}
      />

      <button
        onClick={enhance}
        disabled={loading || !prompt.trim()}
        className="rounded-xl bg-black px-4 py-2 text-white disabled:opacity-50"
      >
        {loading ? "Đang tối ưu..." : "Tối ưu prompt tóc"}
      </button>

      {score && (
        <div className="rounded-xl bg-gray-50 p-3 text-sm">
          <div className="font-semibold">Hair realism score: {score.total}/100 — {score.grade}</div>
          <div className="mt-2 grid grid-cols-2 gap-2">
            <div>Tách sợi: {score.strandSeparation}</div>
            <div>Texture tóc: {score.fiberTexture}</div>
            <div>Tóc con: {score.babyHair}</div>
            <div>Flyaway: {score.flyawayHair}</div>
            <div>Ánh sáng tóc: {score.lightingPhysics}</div>
            <div>Chống tóc nhựa: {score.antiPlasticHair}</div>
          </div>
          {score.issues.length > 0 && (
            <div className="mt-2 text-xs text-red-600">
              <strong>Issues:</strong>
              <ul className="list-disc ml-4">
                {score.issues.map((issue, i) => (
                  <li key={i}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
          {result.gatePassed && (
            <div className="mt-2 rounded-lg bg-green-100 p-2 text-xs text-green-800">
              ✅ Đạt chuẩn render (score ≥ 80)
            </div>
          )}
          {!result.gatePassed && (
            <div className="mt-2 rounded-lg bg-red-100 p-2 text-xs text-red-800">
              ❌ Không đạt chuẩn (score &lt; 80)
            </div>
          )}
        </div>
      )}
    </section>
  );
}
