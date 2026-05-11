"use client";

import { useState } from "react";

import { ImageGallery } from "../../components/design-studio/ImageGallery";
import { InputForm } from "../../components/design-studio/InputForm";
import { OfferPanel } from "../../components/design-studio/OfferPanel";
import { StoryboardPanel } from "../../components/design-studio/StoryboardPanel";
import { UpsellPanel } from "../../components/design-studio/UpsellPanel";
import type { FormState, ImageVariant } from "../../components/design-studio/types";

export default function DesignStudioPage() {
  const [form, setForm] = useState<FormState>({ industry: "my pham", product: "son moi", goal: "sales", channel: "Facebook" });
  const [projectId, setProjectId] = useState<string>("");
  const [traceId, setTraceId] = useState<string>("");
  const [variants, setVariants] = useState<ImageVariant[]>([]);
  const [selected, setSelected] = useState<ImageVariant | null>(null);
  const [upsell, setUpsell] = useState<Record<string, unknown> | null>(null);
  const [scenes, setScenes] = useState<Array<{ scene: number; role: string; prompt: string }>>([]);
  const [offers, setOffers] = useState<Array<{ name: string; price: number; best_for: string }>>([]);
  const [imageJobStatus, setImageJobStatus] = useState<string>("idle");
  const [renderStatus, setRenderStatus] = useState<string>("not_started");

  async function createVideoProject() {
    if (!projectId || !traceId || scenes.length === 0) {
      return;
    }
    setRenderStatus("creating");
    const res = await fetch("/api/v1/render/project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectId,
        trace_id: traceId,
        industry: form.industry,
        product: form.product,
        storyboard: scenes,
      }),
    });
    const json = await res.json();
    setRenderStatus(String(json.data?.status || "failed"));
  }

  async function generate() {
    setImageJobStatus("running");
    const res = await fetch("/api/v1/design/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const json = await res.json();
    setProjectId(String(json.project_id || ""));
    setTraceId(String(json.trace_id || ""));
    const nextVariants = (json.data?.image_variants || []) as ImageVariant[];
    setVariants(nextVariants);
    setImageJobStatus(nextVariants.length > 0 ? "completed" : "failed");
  }

  async function selectVariant(v: ImageVariant) {
    setSelected(v);
    const res = await fetch("/api/v1/design/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectId,
        trace_id: traceId,
        selected_variant: v,
        ...form,
        product_type: "physical",
      }),
    });
    const json = await res.json();
    const workflowData = json.data || {};
    setUpsell((workflowData.upsell || null) as Record<string, unknown> | null);
    setScenes((workflowData.storyboard?.scenes || []) as Array<{ scene: number; role: string; prompt: string }>);
    setOffers((workflowData.offer?.offers || []) as Array<{ name: string; price: number; best_for: string }>);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-6">
      <section className="max-w-6xl mx-auto space-y-6">
        <div className="rounded-2xl bg-neutral-900 p-6 shadow-xl">
          <p className="text-sm text-yellow-300">AI Design-to-Video Operating Environment</p>
          <h1 className="text-3xl font-semibold mt-2">Design Studio</h1>
          <p className="text-neutral-300 mt-2">
            Tao anh, cham diem, phan tich upsell video va dung storyboard preview.
          </p>
          <p className="text-xs text-neutral-400 mt-2">image_job_status: {imageJobStatus}</p>
          {projectId && traceId && (
            <p className="text-xs text-neutral-400 mt-3">project_id: {projectId} | trace_id: {traceId}</p>
          )}
        </div>

        <InputForm form={form} onChange={setForm} onGenerate={generate} />

        <ImageGallery variants={variants} onSelect={selectVariant} />

        {selected && <UpsellPanel upsell={upsell} />}

        <StoryboardPanel scenes={scenes} />

        <OfferPanel offers={offers} />

        {offers.length > 0 && (
          <section className="rounded-2xl bg-neutral-900 p-6">
            <h2 className="text-2xl font-semibold">Checkout / Create Video Project</h2>
            <p className="text-sm text-neutral-400 mt-2">render_status: {renderStatus}</p>
            <button
              onClick={createVideoProject}
              className="mt-4 rounded-xl bg-yellow-400 px-4 py-3 font-semibold text-black"
            >
              Create Video Project
            </button>
          </section>
        )}
      </section>
    </main>
  );
}
