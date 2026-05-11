"use client";

import { useState } from "react";

type ImageVariant = {
  variant_index: number;
  concept_name: string;
  headline: string;
  cta: string;
  layout_direction: string;
  visual_prompt: string;
  scores?: Record<string, number | boolean>;
};

export default function DesignStudioPage() {
  const [form, setForm] = useState({ industry: "mỹ phẩm", product: "son môi", goal: "sales", channel: "Facebook" });
  const [projectId, setProjectId] = useState<string | null>(null);
  const [variants, setVariants] = useState<ImageVariant[]>([]);
  const [selected, setSelected] = useState<ImageVariant | null>(null);
  const [upsell, setUpsell] = useState<any>(null);
  const [storyboard, setStoryboard] = useState<any>(null);
  const [offer, setOffer] = useState<any>(null);

  async function generate() {
    const res = await fetch("/api/v1/design/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const json = await res.json();
    setProjectId(json.data.project_id);
    setVariants(json.data.image_variants);
  }

  async function selectVariant(v: ImageVariant) {
    setSelected(v);
    const res = await fetch("/api/v1/design/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, selected_variant: v, ...form, product_type: "physical" }),
    });
    const json = await res.json();
    setUpsell(json.data.upsell);
    setStoryboard(json.data.storyboard);
    setOffer(json.data.offer);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-6">
      <section className="max-w-6xl mx-auto space-y-6">
        <div className="rounded-2xl bg-neutral-900 p-6 shadow-xl">
          <p className="text-sm text-yellow-300">AI Design-to-Video Operating Environment</p>
          <h1 className="text-3xl font-semibold mt-2">Design Studio</h1>
          <p className="text-neutral-300 mt-2">Tạo ảnh, chấm điểm, phân tích upsell video và dựng storyboard preview.</p>
        </div>

        <div className="grid md:grid-cols-4 gap-3 rounded-2xl bg-neutral-900 p-6">
          {Object.entries(form).map(([key, value]) => (
            <label key={key} className="space-y-2 text-sm text-neutral-300">
              {key}
              <input className="w-full rounded-xl bg-neutral-800 p-3 text-white" value={value} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
            </label>
          ))}
          <button onClick={generate} className="md:col-span-4 rounded-xl bg-yellow-400 px-4 py-3 font-semibold text-black">Generate Image Concepts</button>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {variants.map((v) => (
            <article key={v.variant_index} className="rounded-2xl bg-neutral-900 p-5 space-y-3 border border-neutral-800">
              <div className="aspect-[4/5] rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-700 flex items-center justify-center text-center p-4">
                <span className="text-neutral-300">Image Placeholder<br />{v.concept_name}</span>
              </div>
              <h3 className="text-lg font-semibold">{v.headline}</h3>
              <p className="text-sm text-neutral-400">{v.layout_direction}</p>
              {v.scores && (
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(v.scores).map(([k, val]) => <div key={k} className="rounded-lg bg-neutral-800 p-2">{k}: {String(val)}</div>)}
                </div>
              )}
              <button onClick={() => selectVariant(v)} className="w-full rounded-xl bg-white px-4 py-3 text-black font-semibold">Chọn ảnh này</button>
            </article>
          ))}
        </div>

        {selected && upsell && (
          <section className="rounded-2xl bg-yellow-400 p-6 text-black shadow-xl">
            <h2 className="text-2xl font-bold">Upsell Video Recommendation</h2>
            <p className="mt-2">{upsell.offer_message}</p>
            <p className="mt-2"><b>Loại video:</b> {upsell.video_type} — {upsell.video_length}</p>
            <p className="mt-1"><b>Lý do:</b> {upsell.upsell_reason}</p>
          </section>
        )}

        {storyboard && (
          <section className="rounded-2xl bg-neutral-900 p-6">
            <h2 className="text-2xl font-semibold">Storyboard Preview</h2>
            <div className="grid md:grid-cols-5 gap-3 mt-4">
              {storyboard.scenes.map((s: any) => (
                <div key={s.scene} className="rounded-xl bg-neutral-800 p-4">
                  <p className="text-yellow-300">Scene {s.scene}</p>
                  <h3 className="font-semibold">{s.role}</h3>
                  <p className="text-sm text-neutral-400 mt-2">{s.prompt}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {offer && (
          <section className="rounded-2xl bg-neutral-900 p-6">
            <h2 className="text-2xl font-semibold">Select Video Package</h2>
            <div className="grid md:grid-cols-4 gap-3 mt-4">
              {offer.offers.map((o: any) => (
                <div key={o.name} className="rounded-xl bg-neutral-800 p-4">
                  <h3 className="font-semibold">{o.name}</h3>
                  <p className="text-yellow-300 text-xl mt-2">{o.price.toLocaleString("vi-VN")}đ</p>
                  <p className="text-sm text-neutral-400">{o.best_for}</p>
                </div>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
