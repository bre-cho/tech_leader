"use client";

import { useState } from "react";
import { persistDomainHandoff } from "@/lib/workflow/handoff-client";

type HiDreamPayload = {
  business_goal: string;
  industry: string;
  product_name: string;
  audience?: string;
  use_case?: "beauty_ad" | "fashion_editorial" | "cosmetic_product" | "luxury_perfume" | "poster" | "ecommerce" | "showroom" | "beauty_avatar" | "storyboard_keyframe";
  brand_dna?: Record<string, unknown>;
  visual_dna?: Record<string, unknown>;
  campaign_context?: Record<string, unknown>;
  copy_text?: string;
  aspect_ratio?: "1:1" | "4:5" | "3:4" | "9:16" | "16:9";
  render_tier?: "draft" | "premium" | "hero";
  provider?: "mock" | "hf_inference" | "local_diffusers";
  enable_typography_safe_mode?: boolean;
  enable_storyboard_expansion?: boolean;
  enable_8k_export_contract?: boolean;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const initialPayload: HiDreamPayload = {
  business_goal: "Create a premium cosmetic hero poster that can expand into a product showcase video",
  industry: "cosmetic beauty",
  product_name: "Luminous Serum",
  audience: "young professional women who want premium glowing skin",
  use_case: "cosmetic_product",
  aspect_ratio: "4:5",
  render_tier: "premium",
  provider: "mock",
  copy_text: "Glow that feels premium",
  brand_dna: { palette: "champagne gold, ivory, soft black", temperature: "warm neutral luxury" },
  visual_dna: { materials: "glass serum bottle, liquid refraction, glowing skin, silk fabric" },
  campaign_context: { offer: "launch bundle", channel: "TikTok + landing page" },
  enable_typography_safe_mode: true,
  enable_storyboard_expansion: true,
  enable_8k_export_contract: true,
};

export default function HiDreamCommercialStudio() {
  const [payload, setPayload] = useState<HiDreamPayload>(initialPayload);
  const [brandDna, setBrandDna] = useState(JSON.stringify(initialPayload.brand_dna, null, 2));
  const [visualDna, setVisualDna] = useState(JSON.stringify(initialPayload.visual_dna, null, 2));
  const [campaignContext, setCampaignContext] = useState(JSON.stringify(initialPayload.campaign_context, null, 2));
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const primaryButtonClass =
    "mt-5 rounded-2xl border border-amber-300/60 bg-amber-400 px-5 py-3 font-semibold text-black transition hover:bg-amber-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-200/80 disabled:cursor-not-allowed disabled:border-neutral-600 disabled:bg-neutral-600 disabled:text-neutral-900";

  function parseJson(label: string, value: string) {
    try {
      return JSON.parse(value || "{}");
    } catch {
      throw new Error(`${label} phải là JSON hợp lệ`);
    }
  }

  async function submit() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const finalPayload = {
        ...payload,
        brand_dna: parseJson("brand_dna", brandDna),
        visual_dna: parseJson("visual_dna", visualDna),
        campaign_context: parseJson("campaign_context", campaignContext),
      };
      const response = await fetch(`${API_BASE}/api/v1/hidream/commercial-visual/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(finalPayload),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      setResult(data);

      persistDomainHandoff("hidream-commercial", {
        workflowId: data?.workflow_id || data?.id || undefined,
        request: {
          storyboard: [
            {
              title: payload.product_name,
              description: payload.business_goal,
            },
            {
              title: "Premium visual compile",
              description: payload.copy_text || "HiDream commercial render",
            },
          ],
        },
        providerPayloadResult: data?.prompt_contract || data?.artifact || {},
        videoFlowCompile: data?.videoFlowCompile || { status: data?.promotion_gate?.passed ? "ready" : "hold" },
      });
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function update<K extends keyof HiDreamPayload>(key: K, value: HiDreamPayload[K]) {
    setPayload((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <p className="text-sm text-amber-300">V27 — HiDream Commercial Visual Engine</p>
          <h1 className="mt-2 text-3xl font-bold">Premium Commercial Rendering Layer</h1>
          <p className="mt-2 text-neutral-300">
            Creative Context Graph -&gt; Prompt Compiler -&gt; HiDream Provider -&gt; Artifact Contract -&gt; Perception Scoring -&gt; Storyboard Expansion -&gt; Winner DNA.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="text-xl font-semibold">Business + Creative Input</h2>
            <div className="mt-4 grid gap-3">
              <Field label="business_goal" value={payload.business_goal} onChange={(v) => update("business_goal", v)} />
              <Field label="industry" value={payload.industry} onChange={(v) => update("industry", v)} />
              <Field label="product_name" value={payload.product_name} onChange={(v) => update("product_name", v)} />
              <Field label="audience" value={payload.audience || ""} onChange={(v) => update("audience", v)} />
              <Field label="copy_text" value={payload.copy_text || ""} onChange={(v) => update("copy_text", v)} />
            </div>
            <button onClick={submit} disabled={loading} className={primaryButtonClass}>
              {loading ? "Đang render qua V27..." : "Generate Premium Visual"}
            </button>
            {error ? <p className="mt-3 text-red-300">{error}</p> : null}
          </div>

          <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="text-xl font-semibold">Graph Context JSON</h2>
            <JsonField label="brand_dna" value={brandDna} onChange={setBrandDna} />
            <JsonField label="visual_dna" value={visualDna} onChange={setVisualDna} />
            <JsonField label="campaign_context" value={campaignContext} onChange={setCampaignContext} />
          </div>
        </div>

        {result ? (
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5 lg:col-span-2">
              <h2 className="text-xl font-semibold">Artifact</h2>
              {result.artifact?.url ? (
                <img
                  alt="HiDream artifact"
                  className="mt-3 max-h-[520px] rounded-xl border border-neutral-700"
                  src={String(result.artifact.url).startsWith("/artifacts") ? `${API_BASE}${result.artifact.url}` : result.artifact.url}
                />
              ) : null}
              <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(result.artifact, null, 2)}</pre>
            </div>
            <Panel title="Score + Promotion Gate" data={{ score: result.score, promotion_gate: result.promotion_gate, memory_update: result.memory_update }} />
            <Panel title="Prompt Contract" data={result.prompt_contract} />
          </div>
        ) : null}
      </section>
    </main>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="grid gap-1">
      <span className="text-xs text-neutral-400">{label}</span>
      <input className="rounded-xl border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm" value={value} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}

function JsonField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="mt-3 grid gap-1">
      <span className="text-xs text-neutral-400">{label}</span>
      <textarea className="min-h-24 rounded-xl border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm" value={value} onChange={(e) => onChange(e.target.value)} />
    </label>
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
