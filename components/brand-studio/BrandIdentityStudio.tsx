"use client";

import { useMemo, useState } from "react";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";
import { persistDomainHandoff } from "@/lib/workflow/handoff-client";

type BrandBrief = {
  brandName: string;
  industry: string;
  audience: string;
  personality: string;
  promise: string;
  tagline: string;
  channel: string;
  budgetTier: "low" | "mid" | "premium";
  paletteDirection: string;
  typographyMood: string;
  logoStyle: string;
};

type DesignStudioResult = {
  workflow_id?: string;
  best_concept?: {
    headline?: string;
    prompt?: string;
    score?: number;
    provider_contract?: Record<string, unknown>;
  };
  storyboard?: Array<Record<string, unknown>>;
  promotion_gate?: {
    passed?: boolean;
    reason?: string;
  };
  verification?: {
    score?: number;
    notes?: string[];
  };
  memory_update?: Record<string, unknown>;
  video_concept_preview?: Record<string, unknown>;
};

const defaultBrief: BrandBrief = {
  brandName: "Lumené Beauty",
  industry: "beauty",
  audience: "Nữ 22-35 ưu tiên premium skincare",
  personality: "Tinh tế, hiện đại, đáng tin",
  promise: "Làn da sáng khỏe có cơ sở khoa học",
  tagline: "Glow With Evidence",
  channel: "tiktok,reels,landing-page,store",
  budgetTier: "mid",
  paletteDirection: "warm neutral luxury",
  typographyMood: "editorial sans + contrast serif",
  logoStyle: "minimal monogram + wordmark",
};

const VIDEO_STUDIO_BASE_URL = "https://shiny-memory-gxq4x7jx7xv6fjw9-5173.app.github.dev/";

function encodeJsonToBase64(payload: unknown): string {
  const json = JSON.stringify(payload);
  const bytes = new TextEncoder().encode(json);
  let binary = "";
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index]);
  }
  return btoa(binary);
}

export default function BrandIdentityStudio() {
  const [brief, setBrief] = useState<BrandBrief>(defaultBrief);
  const [result, setResult] = useState<DesignStudioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const identityScore = useMemo(() => {
    if (!result) {
      return 0;
    }
    if (typeof result.verification?.score === "number") {
      return result.verification.score;
    }
    if (typeof result.best_concept?.score === "number") {
      return result.best_concept.score;
    }
    return 88;
  }, [result]);

  const applicationItems = useMemo(() => {
    return brief.channel
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  }, [brief.channel]);

  const update = <K extends keyof BrandBrief>(key: K, value: BrandBrief[K]) => {
    setBrief((current) => ({ ...current, [key]: value }));
  };

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/v1/design-studio/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          industry: brief.industry,
          product: `${brief.brandName} Brand Identity System`,
          audience: brief.audience,
          channel: brief.channel,
          goal: `${brief.promise}. Personality: ${brief.personality}. Tagline: ${brief.tagline}`,
          brand_name: brief.brandName,
          budget_tier: brief.budgetTier,
          dry_run: false,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Brand studio run failed.");
      }

      const data = (await response.json()) as DesignStudioResult;
      setResult(data);

      persistDomainHandoff("brand-studio", {
        workflowId: data.workflow_id,
        request: {
          storyboard: data.storyboard || [
            {
              title: "Brand identity direction",
              description: data.best_concept?.headline || data.best_concept?.prompt || brief.promise,
            },
          ],
        },
        providerPayloadResult: {
          best_concept: data.best_concept || {},
          preview: data.video_concept_preview || {},
        },
        videoFlowCompile: {
          status: data.promotion_gate?.passed ? "ready" : "hold",
          verification: data.verification || {},
        },
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Khong the chay Brand Studio.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const openVideoStudio = () => {
    const local = localStorage.getItem("handoff:brand-studio:latest");
    const nextUrl = new URL(VIDEO_STUDIO_BASE_URL);
    nextUrl.searchParams.set("source", "brand-studio");
    nextUrl.searchParams.set("render", "video");
    if (local) {
      nextUrl.searchParams.set("handoff", encodeJsonToBase64(JSON.parse(local)));
    }
    window.location.assign(nextUrl.toString());
  };

  const heroTitle = result?.best_concept?.headline || `${brief.brandName} Identity System`;
  const heroSubline = result?.best_concept?.prompt || brief.promise;

  return (
    <main className="min-h-screen bg-[#f3eee6] text-[#241f19]">
      <section className="mx-auto max-w-[1240px] px-4 py-4 md:px-6 md:py-6 lg:px-8 lg:py-8">
        <div className="rounded-[24px] border border-[#d8c8b2] bg-gradient-to-br from-[#fff8ee] via-[#f8efe3] to-[#f2e4d5] p-5 shadow-[0_22px_70px_rgba(62,37,10,0.12)] md:rounded-[28px] md:p-6 lg:rounded-[32px] lg:p-8">
          <p className="text-[10px] uppercase tracking-[0.3em] text-[#8d6234] md:text-[11px]">Brand Studio</p>
          <h1 className="mt-3 text-[34px] leading-[0.98] md:text-[48px] md:leading-[1] lg:text-[64px]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
            Brand Identity Control Board
          </h1>
          <p className="mt-3 max-w-3xl text-[13px] leading-6 text-[#5f4a37] md:mt-4 md:text-[15px] md:leading-7 lg:text-base">
            Bản vòng 2 tập trung nhịp layout và visual hierarchy theo studio mẫu:
            khối brief bên trái, bảng nhận diện thương hiệu live bên phải,
            spacing thoáng và màu vật liệu thiên hướng editorial.
          </p>
          <div className="mt-4 flex flex-wrap gap-2 md:mt-5">
            <span className="rounded-full border border-[#d4b28a] bg-[#fff5e6] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[#8d6234]">Logo</span>
            <span className="rounded-full border border-[#d4b28a] bg-[#fff5e6] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[#8d6234]">Palette</span>
            <span className="rounded-full border border-[#d4b28a] bg-[#fff5e6] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[#8d6234]">Typography</span>
            <span className="rounded-full border border-[#d4b28a] bg-[#fff5e6] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[#8d6234]">Channel Kit</span>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1240px] gap-4 px-4 pb-8 md:gap-6 md:px-6 md:pb-10 lg:grid-cols-[560px_1fr] lg:gap-8 lg:px-8 lg:pb-12">
        <div className="space-y-4 md:space-y-6">
          <div className="rounded-[22px] border border-[#d8c8b2] bg-white p-4 shadow-[0_18px_44px_rgba(44,24,8,0.08)] md:rounded-[24px] md:p-5 lg:min-h-[760px] lg:rounded-[28px] lg:p-6">
            <div className="mb-5 flex items-end justify-between gap-3">
              <div>
                <p className="text-[10px] uppercase tracking-[0.24em] text-[#8d6234] md:text-[11px]">Creative Brief</p>
                <h2 className="mt-2 text-[24px] leading-[1.05] md:text-[28px] lg:text-[30px]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
                  Thiết lập đầu vào nhận diện
                </h2>
              </div>
              <div className="rounded-xl border border-[#e3d4c2] bg-[#faf3ea] px-3 py-2 text-right text-[11px] text-[#7a6046] md:text-xs">
                <div>Status</div>
                <div className="font-semibold text-[#5d4227]">{loading ? "Running" : "Ready"}</div>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 md:gap-4">
              <Field label="Brand name" value={brief.brandName} onChange={(value) => update("brandName", value)} />
              <Field label="Industry" value={brief.industry} onChange={(value) => update("industry", value)} />
              <Field label="Audience" value={brief.audience} onChange={(value) => update("audience", value)} />
              <Field label="Personality" value={brief.personality} onChange={(value) => update("personality", value)} />
              <Field label="Brand promise" value={brief.promise} onChange={(value) => update("promise", value)} />
              <Field label="Tagline" value={brief.tagline} onChange={(value) => update("tagline", value)} />
              <Field label="Channel list" value={brief.channel} onChange={(value) => update("channel", value)} />
              <Field label="Palette direction" value={brief.paletteDirection} onChange={(value) => update("paletteDirection", value)} />
              <Field label="Typography mood" value={brief.typographyMood} onChange={(value) => update("typographyMood", value)} />
              <Field label="Logo style" value={brief.logoStyle} onChange={(value) => update("logoStyle", value)} />
              <label className="grid gap-2">
                <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">Budget tier</span>
                <select
                  className="rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 py-2 text-sm text-[#2f2419]"
                  value={brief.budgetTier}
                  onChange={(event) => update("budgetTier", event.target.value as BrandBrief["budgetTier"])}
                >
                  <option value="low">low</option>
                  <option value="mid">mid</option>
                  <option value="premium">premium</option>
                </select>
              </label>
            </div>

            <div className="mt-5 flex flex-wrap gap-2.5 md:mt-6 md:gap-3">
              <button
                className="rounded-2xl bg-[#22170f] px-4 py-2.5 text-sm font-semibold text-[#f4e8d8] transition hover:bg-[#302117] md:px-5 md:py-3"
                type="button"
                onClick={run}
                disabled={loading}
              >
                {loading ? "Dang tao identity..." : "Start Brand Studio"}
              </button>
              <button
                className="rounded-2xl border border-[#cfb28f] bg-[#fff5e7] px-4 py-2.5 text-sm font-semibold text-[#6c4b2b] md:px-5 md:py-3"
                type="button"
                onClick={openVideoStudio}
              >
                Open Video Studio (5173)
              </button>
            </div>

            {error ? (
              <div className="mt-4 rounded-xl border border-red-700/20 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}
          </div>

          <OperationFlowBridge sourceKey="brand-studio" title="BRAND IDENTITY OPERATION FLOW" theme="brand-studio" />
        </div>

        <div className="space-y-4 md:space-y-6">
          <div className="rounded-[22px] border border-[#d8c8b2] bg-[#20170f] p-5 text-[#f3e7d7] shadow-[0_20px_56px_rgba(22,12,5,0.22)] md:rounded-[24px] md:p-6 lg:min-h-[520px] lg:rounded-[28px] lg:p-7">
            <p className="text-[10px] uppercase tracking-[0.26em] text-[#d8b48a] md:text-[11px]">Live Brand Board</p>
            <h2 className="mt-3 text-[30px] leading-[1.04] md:text-[38px] lg:text-[44px]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
              {heroTitle}
            </h2>
            <p className="mt-3 text-[13px] leading-6 text-[#d9c6b1] md:text-[14px] md:leading-7">{heroSubline}</p>

            <div className="mt-5 grid gap-3 sm:grid-cols-3 md:mt-6">
              <ColorSwatch hex="#F7E8D0" label="Base" />
              <ColorSwatch hex="#CB9A53" label="Accent" />
              <ColorSwatch hex="#17110A" label="Contrast" />
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 md:mt-6">
              <div className="rounded-2xl border border-[#4a3522] bg-[#2a1d12] p-4 md:min-h-[132px]">
                <div className="text-[11px] uppercase tracking-[0.2em] text-[#c49a70]">Identity Score</div>
                <div className="mt-2 text-[42px] leading-none font-semibold text-[#f2d9b3] md:text-[52px]">{identityScore || "--"}</div>
              </div>
              <div className="rounded-2xl border border-[#4a3522] bg-[#2a1d12] p-4 md:min-h-[132px]">
                <div className="text-[11px] uppercase tracking-[0.2em] text-[#c49a70]">Promotion Gate</div>
                <div className="mt-2 text-lg font-semibold text-[#f2d9b3] md:text-xl">
                  {result?.promotion_gate?.passed ? "Ready for rollout" : "Need refinement"}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-[22px] border border-[#d8c8b2] bg-white p-5 shadow-[0_18px_40px_rgba(41,22,7,0.08)] md:rounded-[24px] md:p-6 lg:rounded-[28px]">
            <h3 className="text-[22px] leading-tight md:text-[24px]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
              Channel Application Kit
            </h3>
            <div className="mt-4 flex flex-wrap gap-2.5">
              {applicationItems.map((item) => (
                <span key={item} className="rounded-full border border-[#d8b48a] bg-[#fff6ea] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[#8d6234]">
                  {item}
                </span>
              ))}
            </div>
            <pre className="mt-4 max-h-[280px] overflow-auto rounded-2xl border border-[#e7d9c8] bg-[#f9f4ec] p-3 text-xs leading-6 text-[#5b4531] md:max-h-[320px]">
              {JSON.stringify(
                {
                  workflow_id: result?.workflow_id,
                  verification: result?.verification,
                  memory_update: result?.memory_update,
                },
                null,
                2,
              )}
            </pre>
          </div>
        </div>
      </section>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2">
      <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">{label}</span>
      <input
        className="h-11 rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 py-2 text-sm text-[#2f2419] md:h-12"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ColorSwatch({ hex, label }: { hex: string; label: string }) {
  return (
    <div className="overflow-hidden rounded-xl border border-[#4a3522] bg-[#1b120b] md:min-h-[98px]">
      <div className="h-10 md:h-11" style={{ backgroundColor: hex }} />
      <div className="px-2 py-2 text-[11px] text-[#e7d0b2] md:px-3 md:py-2.5">
        <div>{label}</div>
        <div>{hex}</div>
      </div>
    </div>
  );
}
