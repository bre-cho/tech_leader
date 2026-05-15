const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

export type DesignRequest = {
  industry: string;
  product: string;
  audience: string;
  channel: string;
  goal: string;
  brand_name: string;
  tone?: string;
  budget_tier?: 'low' | 'mid' | 'premium';
  language?: string;
  dry_run?: boolean;
};

export type DesignResponse = {
  workflow_id: string;
  dry_run: boolean;
  promotion_mode: 'REAL' | 'DRY_RUN';
  technical_lead_plan: Record<string, unknown>;
  best_concept: { headline: string; prompt: string; score?: Record<string, unknown> };
  upsell_analysis: { offer_message?: string } & Record<string, unknown>;
  storyboard: Array<{ scene_id: string; title: string; visual_prompt: string }>;
  offer_packages: Array<{ package: string; price_hint: string; deliverable: string }>;
  verification: Record<string, unknown>;
  promotion_gate: { status: string };
  memory_update: Record<string, unknown>;
};

export async function runDesignStudio(payload: DesignRequest): Promise<DesignResponse> {
  const res = await fetch(`${API_BASE}/design-studio/run`, {
    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<DesignResponse>;
}

export async function getOperatingLaw() {
  const res = await fetch(`${API_BASE}/governance/operating-law`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
