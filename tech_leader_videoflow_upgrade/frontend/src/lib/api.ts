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
};

export async function runDesignStudio(payload: DesignRequest) {
  const res = await fetch(`${API_BASE}/design-studio/run`, {
    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getOperatingLaw() {
  const res = await fetch(`${API_BASE}/governance/operating-law`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
