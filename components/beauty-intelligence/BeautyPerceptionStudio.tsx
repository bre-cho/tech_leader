"use client";
import {useState} from "react";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function BeautyPerceptionStudio() {
  const [file, setFile] = useState<File | null>(null);
  const [preset, setPreset] = useState("soft_glam");
  const [persona, setPersona] = useState("kol_beauty");
  const [data, setData] = useState<any>(null);
  const [graph, setGraph] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run(endpoint="transfer") {
    if (!file) return alert("Upload ảnh trước");
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    form.append("brand_name", "Demo Beauty");
    form.append("persona", persona);
    form.append("preset", preset);
    form.append("strength", "0.6");
    form.append("skin_preservation", "true");
    form.append("identity_preservation", "true");
    form.append("export_scale", "preview");
    const res = await fetch(`${API}/api/v1/beauty/${endpoint}`, {method:"POST", body:form});
    setData(await res.json());
    const g = await fetch(`${API}/api/v1/beauty/graph`);
    setGraph(await g.json());
    setLoading(false);
  }

  const presets = ["natural_clean","soft_glam","korean_bridal","luxury_editorial","clinic_trust","tiktok_fresh"];
  const personas = ["personal_beauty","kol_beauty","wedding","studio_makeup","spa","cosmetic_brand","beauty_clinic","tiktok_creator"];

  return (
    <main style={{minHeight:"100vh", background:"#070707", color:"#fff", padding:32, fontFamily:"Inter, sans-serif"}}>
      <h1>V26 — AI Beauty / Makeup / Face Perception Intelligence</h1>
      <p>Không phải makeup filter. Đây là Beauty Perception Operating System.</p>

      <input type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0] || null)} />
      <div style={{display:"flex", gap:12, marginTop:16, flexWrap:"wrap"}}>
        <select value={preset} onChange={e=>setPreset(e.target.value)}>{presets.map(p=><option key={p}>{p}</option>)}</select>
        <select value={persona} onChange={e=>setPersona(e.target.value)}>{personas.map(p=><option key={p}>{p}</option>)}</select>
        <button onClick={()=>run("analyze")} disabled={loading}>Analyze</button>
        <button onClick={()=>run("transfer")} disabled={loading}>{loading ? "Đang xử lý..." : "Transfer Makeup"}</button>
      </div>

      {data && (
        <section style={{display:"grid", gap:16, marginTop:24}}>
          <Card title="QA" text={JSON.stringify(data.qa, null, 2)} />
          <Card title="Skin Tone Intelligence" text={JSON.stringify(data.skin_tone, null, 2)} />
          <Card title="Color Neutralization Graph" text={JSON.stringify(data.color_neutralization, null, 2)} />
          <Card title="Contour / Highlight" text={JSON.stringify(data.contour_highlight, null, 2)} />
          <Card title="Semantic Makeup Transfer" text={JSON.stringify(data.makeup_transfer, null, 2)} />
          <Card title="Beauty Perception" text={JSON.stringify(data.beauty_perception, null, 2)} />
          <p>Output path: {data.output_path}</p>
        </section>
      )}

      {graph && (
        <section style={{marginTop:24}}>
          <h2>Beauty Perception Graph</h2>
          {graph.items.slice(0,10).map((e:any, i:number)=>(
            <div key={i} style={{border:"1px solid #222", padding:12, borderRadius:12, marginBottom:8}}>
              {e.source} → {e.relation} → {e.target} | {Number(e.weight).toFixed(2)}
            </div>
          ))}
        </section>
      )}
    </main>
  );
}

function Card({title,text}:{title:string;text:string}) {
  return <div style={{border:"1px solid #333", borderRadius:16, padding:16}}>
    <h2>{title}</h2><pre style={{whiteSpace:"pre-wrap"}}>{text}</pre>
  </div>
}
