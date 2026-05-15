"use client";

import { useState } from "react";

export default function BeautyCommercePage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/beauty-commerce/v28/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty",
        productName: "Glow Serum",
        productType: "serum bottle",
        industry: "cosmetic_brand",
        targetAudience: "Vietnamese women 22-35",
        campaignGoal: "conversion",
        channel: "tiktok",
        avatarDescription: "realistic virtual Asian beauty KOL, natural skin texture, premium makeup glow",
        outfitStyle: "elegant luxury fashion styling, tasteful soft feminine commercial look",
        poseGoal: "product_demo",
        sensualityLevel: "soft",
        references: [],
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="brain-route-main">
      <section className="brain-route-wrap">
        <div className="brain-route-head">
          <p className="brain-route-kicker">V28 Runtime</p>
          <h1 className="brain-route-title">Beauty Commerce Engine</h1>
          <p className="brain-route-desc">
            Beauty Persona to Facial Consistency to Fashion Perception to Provider Router,
            verification, and Winner DNA update in one execution flow.
          </p>
        </div>

        <div className="brain-action-row">
          <button onClick={run} disabled={loading} className="brain-primary-btn">
            {loading ? "Đang chạy V28..." : "Run Beauty Commerce Engine"}
          </button>
        </div>

        {result && (
          <pre className="rounded-2xl border border-neutral-800 bg-neutral-900 p-4 whitespace-pre-wrap text-sm text-neutral-300">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </section>
    </main>
  );
}
