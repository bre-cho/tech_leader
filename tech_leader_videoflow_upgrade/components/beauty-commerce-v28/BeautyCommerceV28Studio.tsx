"use client";

import { useState } from "react";

export default function BeautyCommerceV28Studio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/beauty-commerce/v28-2/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty",
        productName: "Glow Serum",
        productType: "serum bottle",
        industry: "tiktok_beauty_ads",
        avatarDna: "realistic Vietnamese/Asian beauty KOL, natural skin texture, soft feminine commercial look, warm smile, premium makeup glow",
        campaignGoal: "conversion",
        channel: "tiktok",
        sceneCount: 5,
        durationSec: 15,
        references: [
          { kind: "identity", label: "Avatar face ref", uri: "/refs/avatar.png", lockStrength: 0.92 },
          { kind: "makeup", label: "K-beauty makeup ref", uri: "/refs/makeup.png", lockStrength: 0.85 },
          { kind: "lighting", label: "warm lifestyle lighting", uri: "/refs/lighting.png", lockStrength: 0.8 }
        ],
        outputDir: "storage/beauty-commerce-v28/demo",
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-6xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V28.2 + V28.3 Beauty Commerce Engine</h1>
          <p className="mt-2 text-neutral-300">
            Banana Multi-Reference + Femininity Commerce + Social Beauty Commerce Video runtime.
          </p>
          <button onClick={run} disabled={loading} className="mt-5 rounded-2xl bg-white px-5 py-3 font-semibold text-black">
            {loading ? "Đang chạy engine..." : "Run V28.2 / V28.3"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Commercial Score" data={{ status: result.status, commercialScore: result.commercialScore, verification: result.verification }} />
            <Panel title="Provider Payloads" data={result.providerPayloads} />
            <Panel title="Video Plan" data={result.videoPlan} />
            <Panel title="Winner DNA" data={result.winnerDna ?? "Not promoted yet"} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Prompt</h2>
              <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{result.prompt}</pre>
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
