"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ImageDesignWorkforcePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch(`${API}/api/v1/workforce/image-design/run`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        save_memory: true,
        brief: {
          brand_name: "Demo Beauty",
          industry: "beauty",
          product_name: "Glow Serum",
          product_type: "serum bottle",
          target_audience: "Vietnamese women 22-35",
          campaign_goal: "conversion",
          channel: "tiktok",
          offer: "Try mini serum today",
          brand_tone: "premium, trustworthy, luxury"
        }
      })
    });
    setData(await res.json());
    setLoading(false);
  }

  return (
    <main style={{minHeight:"100vh", background:"#080808", color:"#fff", padding:32, fontFamily:"Inter, sans-serif"}}>
      <h1>Multi-Agent Image Design Workforce</h1>
      <p>Creative Director + Visual Strategist + Composition + Typography + Brand + Conversion + Motion + Industry + QA</p>
      <button onClick={run} disabled={loading} style={{padding:"12px 18px", borderRadius:12}}>
        {loading ? "Đang chạy workforce..." : "Run Workforce"}
      </button>
      {data && (
        <section style={{marginTop:24, display:"grid", gap:16}}>
          <Card title="Promotion" text={`${data.promotion_status} — score ${data.verification_score}`} />
          <Card title="Winner DNA" text={JSON.stringify(data.winner_dna, null, 2)} />
          <Card title="Agents" text={data.agent_results.map((a:any)=>a.agent_name).join(" → ")} />
          <pre style={{whiteSpace:"pre-wrap", background:"#111", padding:16, borderRadius:16}}>{data.final_prompt}</pre>
        </section>
      )}
    </main>
  );
}

function Card({title, text}:{title:string; text:string}) {
  return <div style={{border:"1px solid #333", borderRadius:16, padding:16}}><h2>{title}</h2><pre style={{whiteSpace:"pre-wrap"}}>{text}</pre></div>
}
