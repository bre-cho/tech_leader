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
    <main style={{minHeight:"100vh", background:"#080808", color:"#fff", padding:32, fontFamily:"Inter, sans-serif"}}>
      <h1>V28 — Beauty Commerce Engine</h1>
      <p>Beauty Persona → Facial Consistency → Fashion Perception → Provider Router → Verification → Winner DNA</p>
      <button onClick={run} disabled={loading} style={{padding:"12px 18px", borderRadius:12}}>
        {loading ? "Đang chạy V28..." : "Run Beauty Commerce Engine"}
      </button>
      {result && <pre style={{whiteSpace:"pre-wrap", background:"#111", padding:16, borderRadius:16, marginTop:24}}>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}
