'use client';
import { useState } from 'react';
import { CommercialReasoningPanel } from '@/components/commercial/CommercialReasoningPanel';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function CommercialCreativePage(){
  const [result,setResult]=useState<any>(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState<string | null>(null);

  async function run(){
    setLoading(true);
    setError(null);
    const payload={brand_name:'Lumi',product_name:'Gold Serum',category:'beauty',audience:'premium skincare buyers',business_goal:'conversion',product_benefits:['glowing skin','hydration','premium texture'],export_targets:['social','print'],product_materials:['glass','liquid'],price_tier:'luxury'};
    try {
      let r=await fetch('/api/commercial-intelligence/reason',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if (!r.ok) {
        r = await fetch(`${API_BASE}/api/v1/commercial-intelligence/reason`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      }
      if (!r.ok) {
        const failure = await r.json().catch(() => ({ error: `Request failed (${r.status})` }));
        throw new Error(failure.error || `Request failed (${r.status})`);
      }
      setResult(await r.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }
  return <main className="brain-route-main">
    <div className="brain-route-wrap">
      <section className="brain-route-head">
        <p className="brain-route-kicker">V27.1 to V27.7</p>
        <h1 className="brain-route-title">AI Commercial Creative Infrastructure</h1>
        <p className="brain-route-desc">
          Commercial visual reasoning, attention routing, typography planning, product hero strategy,
          psychology mapping, and billboard or print readiness in one flow.
        </p>
      </section>

      <div className="brain-action-row">
        <button onClick={run} className="brain-primary-btn" disabled={loading}>
          {loading ? 'Đang phân tích...' : 'Run Commercial Reasoning'}
        </button>
      </div>

      {error && <p className="brain-warning-text">{error}. Backend có thể chưa khởi động ở cổng 8000.</p>}
      {result && <CommercialReasoningPanel result={result}/>}
    </div>
  </main>
}
