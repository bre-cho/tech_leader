import React, { useEffect, useState } from 'react';
import { runDesignStudio, getOperatingLaw, DesignRequest, DesignResponse } from '../lib/api';

const initial: DesignRequest = {
  industry: 'spa mỹ phẩm',
  product: 'serum phục hồi da',
  audience: 'phụ nữ 25-35',
  channel: 'TikTok',
  goal: 'bán hàng',
  brand_name: 'Lumi Skin',
  budget_tier: 'mid',
  language: 'vi',
};

export default function DesignStudio() {
  const [form, setForm] = useState<DesignRequest>(initial);
  const [law, setLaw] = useState<any>(null);
  const [result, setResult] = useState<DesignResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { getOperatingLaw().then(setLaw).catch(() => null); }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setLoading(true); setError(''); setResult(null);
    try { setResult(await runDesignStudio(form)); } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  }

  function field(name: keyof DesignRequest, label: string) {
    return <label><span>{label}</span><input value={(form[name] as string) || ''} onChange={e=>setForm({...form,[name]:e.target.value})}/></label>
  }

  return <main className="page">
    <section className="hero">
      <div>
        <p className="eyebrow">Agentic Creative Operating Environment</p>
        <h1>Design Studio → Image Scoring → Video Upsell → Storyboard → Winner DNA</h1>
        <p className="sub">MVP vận hành theo hard law: workflow-first, agent-driven, memory-backed, verification-gated.</p>
      </div>
      <div className="law-card"><b>Promotion Gate</b><span>{result?.promotion_gate?.status || 'Chưa chạy'}</span></div>
    </section>

    {law && <section className="panel small"><b>CORE LAW:</b><pre>{law.required_steps.join(' → ')}</pre></section>}

    <form className="panel form" onSubmit={submit}>
      {field('industry','Ngành')}{field('product','Sản phẩm/Dịch vụ')}{field('audience','Khách hàng mục tiêu')}{field('channel','Kênh')}{field('goal','Mục tiêu')}{field('brand_name','Tên thương hiệu')}
      <label><span>Dry run</span><input type="checkbox" checked={!!form.dry_run} onChange={e=>setForm({...form,dry_run:e.target.checked})}/></label>
      <button disabled={loading}>{loading ? 'Đang chạy agent runtime...' : 'Run Design-to-Video Workflow'}</button>
      {error && <p className="error">{error}</p>}
    </form>

    {result && <section className="grid">
      <div className="panel"><h2>Technical Lead Plan</h2><pre>{JSON.stringify(result.technical_lead_plan, null, 2)}</pre></div>
      <div className="panel"><h2>Best Concept</h2><h3>{result.best_concept.headline}</h3><p>{result.best_concept.prompt}</p><pre>{JSON.stringify(result.best_concept.score, null, 2)}</pre></div>
      <div className="panel"><h2>Upsell Analyzer</h2><p>{result.upsell_analysis.offer_message ?? ''}</p><pre>{JSON.stringify(result.upsell_analysis, null, 2)}</pre></div>
      <div className="panel"><h2>Storyboard</h2>{result.storyboard.map((s:any)=><div className="scene" key={s.scene_id}><b>{s.scene_id} — {s.title}</b><p>{s.visual_prompt}</p></div>)}</div>
      <div className="panel"><h2>Offer Packages</h2>{result.offer_packages.map((o:any)=><div className="offer" key={o.package}><b>{o.package}</b><span>{o.price_hint}</span><p>{o.deliverable}</p></div>)}</div>
      <div className="panel"><h2>Verification + Memory</h2><pre>{JSON.stringify({verification: result.verification, promotion_gate: result.promotion_gate, memory_update: result.memory_update}, null, 2)}</pre></div>
    </section>}
  </main>
}
