"use client";

import { useState } from "react";

export default function IdentityBeautyRuntimeStudio() {
  const [result, setResult] = useState<any>(null);
  const [visualIntent, setVisualIntent] = useState("luxury_tropical_cafe");
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/beauty-identity/v29-1/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty OS",
        campaignName: "identity_lock_campaign",
        visualIntent,
        platform: "poster",
        provider: "auto",
        references: [
          { id: "face_ref_001", kind: "face", uri: "/refs/face.png", lockStrength: 0.96 },
          { id: "makeup_ref_001", kind: "makeup", uri: "/refs/makeup.png", lockStrength: 0.88 },
          { id: "pose_ref_001", kind: "pose", uri: "/refs/pose.png", lockStrength: 0.82 }
        ],
        product: {
          name: "Luxury Lipstick",
          category: "cosmetics"
        },
        faceLock: {
          enabled: true,
          strictness: 0.96,
          preserveMoleMap: true,
          preserveSkinTexture: true,
          preserveNaturalAsymmetry: true
        },
        output: {
          aspectRatio: "4:5",
          quality: "8K",
          outputDir: "storage/v29-1-identity-lock/demo"
        },
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V29.1 — Identity Lock Beauty Runtime</h1>
          <p className="mt-2 text-neutral-300">Face Lock → Visual Recipe → Provider Route → Prompt Pack → QA Gate → Winner DNA.</p>
          <div className="mt-5 flex gap-3">
            <select className="rounded-xl bg-neutral-800 p-3" value={visualIntent} onChange={e => setVisualIntent(e.target.value)}>
              <option value="luxury_tropical_cafe">Luxury Tropical Cafe</option>
              <option value="korean_street_fashion">Korean Street Fashion</option>
              <option value="sporty_wildcats_campaign">Sporty WildCats</option>
              <option value="luxury_lipstick_ad">Luxury Lipstick Ad</option>
              <option value="cinematic_car_wash">Cinematic Car Wash</option>
            </select>
            <button onClick={run} disabled={loading} className="btn-primary">
              {loading ? "Đang chạy..." : "Run Runtime"}
            </button>
          </div>
        </div>

        {result && (
          <>
            <Panel title="Status + QA" data={{ status: result.status, qa: result.qaReport }} />
            <Panel title="Provider Route" data={result.providerRoute} />
            <Panel title="Visual Recipe" data={result.visualRecipe} />
            <Panel title="Provider Payloads" data={result.providerPayloads} />
            <Panel title="Winner DNA" data={result.winnerDna ?? "Not saved"} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Prompt Pack</h2>
              <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(result.promptPack.data, null, 2)}</pre>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

function Panel({ title, data }: { title: string; data: any }) {
  return (
    <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
      <h2 className="text-xl font-semibold">{title}</h2>
      <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
