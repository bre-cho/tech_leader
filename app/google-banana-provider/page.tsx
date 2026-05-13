"use client";

import { useState } from "react";

export default function GoogleBananaProviderPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/providers/google-banana/commercial-poster", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        model: "gemini-3.1-flash-image-preview",
        prompt: "Luxury beauty commercial poster for a premium serum bottle, clear product hero, readable headline area, warm champagne lighting, natural Asian skin texture, clean CTA zone, billboard and TikTok ready.",
        aspectRatio: "4:5",
        resolution: "2K",
        outputDir: "storage/google-banana/demo",
        metadata: {
          brand: "Demo Beauty",
          workflow: "commercial_poster"
        }
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main style={{minHeight:"100vh", background:"#080808", color:"#fff", padding:32, fontFamily:"Inter, sans-serif"}}>
      <h1>Google Banana Provider</h1>
      <p>Commercial default provider for poster, TikTok creative, multi-reference and brand-consistent campaigns.</p>
      <button onClick={run} disabled={loading} style={{padding:"12px 18px", borderRadius:12}}>
        {loading ? "Đang generate..." : "Run Commercial Poster"}
      </button>
      {result && <pre style={{whiteSpace:"pre-wrap", background:"#111", padding:16, borderRadius:16, marginTop:24}}>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}
