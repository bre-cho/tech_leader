"use client";

import { useMemo, useState, type ChangeEvent } from "react";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";
import { persistDomainHandoff } from "@/lib/workflow/handoff-client";

type UpscaleResult = {
  status?: string;
  mode?: string;
  model?: string;
  textParts?: string[];
  artifacts?: Array<{
    artifactId?: string;
    type?: string;
    path?: string;
    mimeType?: string;
    sizeBytes?: number;
  }>;
  scoring?: Record<string, unknown>;
};

type UpscalePreset = "social_4k" | "print_8k";

const models = [
  "gemini-3.1-flash-image-preview",
  "gemini-3-pro-image-preview",
  "gemini-2.5-flash-image",
] as const;

export default function UpscaleStudio() {
  const [sourceImageDataUrl, setSourceImageDataUrl] = useState("");
  const [sourceFileName, setSourceFileName] = useState("source-image.png");
  const [model, setModel] = useState<(typeof models)[number]>("gemini-3.1-flash-image-preview");
  const [preset, setPreset] = useState<UpscalePreset>("social_4k");
  const [prompt, setPrompt] = useState(
    "Upscale and refine this commercial key visual while preserving identity, product shape, brand typography layout, skin texture realism, and premium lighting fidelity.",
  );
  const [result, setResult] = useState<UpscaleResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sourceImageBase64 = useMemo(() => {
    if (!sourceImageDataUrl.includes(",")) {
      return "";
    }
    return sourceImageDataUrl.split(",")[1] || "";
  }, [sourceImageDataUrl]);

  const artifactImage = useMemo(() => {
    const imageArtifact = result?.artifacts?.find((item) => item?.type === "image");
    return imageArtifact ?? null;
  }, [result]);

  const resultSummary = useMemo(() => {
    if (!result) {
      return "Chua co ket qua upscale.";
    }
    const totalArtifacts = result.artifacts?.length || 0;
    return `${result.status || "unknown"} · ${result.mode || "upscale"} · ${totalArtifacts} artifacts`;
  }, [result]);

  const handleUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const value = typeof reader.result === "string" ? reader.result : "";
      setSourceImageDataUrl(value);
      setSourceFileName(file.name || "source-image.png");
    };
    reader.readAsDataURL(file);
  };

  const runUpscale = async () => {
    if (!sourceImageBase64) {
      setError("Vui long upload anh truoc khi upscale.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/providers/google-banana/8k-upscale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          prompt,
          negativePrompt:
            "identity drift, blurry text, changed logo, broken product geometry, over-smoothing, noisy edges",
          aspectRatio: "4:5",
          resolution: "4K",
          outputDir: "storage/google-banana/upscale-studio",
          images: [
            {
              mimeType: sourceImageDataUrl.includes("image/jpeg") ? "image/jpeg" : "image/png",
              dataBase64: sourceImageBase64,
              label: "upscale-source",
            },
          ],
          metadata: {
            workflow: "upscale-studio",
            preset,
            target_final: preset === "print_8k" ? "8K" : "4K",
            file_name: sourceFileName,
          },
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Upscale request failed.");
      }

      const data = (await response.json()) as UpscaleResult;
      setResult(data);

      const storyboard = [
        {
          title: "Input image ingest",
          description: sourceFileName,
        },
        {
          title: "AI upscale refinement",
          description: `${preset === "print_8k" ? "8K print" : "4K social"} preset via ${model}`,
        },
        {
          title: "Artifact export",
          description: `${data.artifacts?.length || 0} artifacts written`,
        },
      ];

      persistDomainHandoff("upscale", {
        workflowId: data.artifacts?.[0]?.artifactId || undefined,
        request: { storyboard },
        providerPayloadResult: {
          status: data.status,
          model: data.model,
          scoring: data.scoring,
        },
        videoFlowCompile: {
          status: data.status || "ready",
          artifacts: data.artifacts || [],
        },
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upscale request failed.";
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f5f1ea] text-[#1f1812]">
      <section className="mx-auto max-w-[1240px] px-4 py-5 md:px-6 md:py-6 lg:px-8 lg:py-8">
        <div className="rounded-[24px] border border-[#deccb7] bg-gradient-to-br from-[#fff9f0] via-[#f8efe4] to-[#f1e4d5] p-5 shadow-[0_22px_70px_rgba(56,36,16,0.13)] md:p-6 lg:p-8">
          <p className="text-[10px] uppercase tracking-[0.32em] text-[#8f6133]">Upscale Studio</p>
          <h1
            className="mt-3 text-[34px] leading-[0.98] md:text-[50px] lg:text-[66px]"
            style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}
          >
            AI Image Upscale 4K / 8K
          </h1>
          <p className="mt-3 max-w-3xl text-[13px] leading-6 text-[#654c35] md:text-[15px] md:leading-7">
            Nâng cấp ảnh thương mại theo workflow upload - enhance - verify - export.
            Layout tập trung so sánh before/after và control panel giống studio mẫu.
          </p>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1240px] gap-4 px-4 pb-8 md:gap-6 md:px-6 lg:grid-cols-[560px_1fr] lg:gap-8 lg:px-8 lg:pb-12">
        <div className="space-y-4 md:space-y-6">
          <div className="rounded-[22px] border border-[#d8c8b2] bg-white p-4 shadow-[0_18px_44px_rgba(44,24,8,0.08)] md:p-5 lg:p-6">
            <div className="mb-4 flex items-end justify-between gap-3">
              <div>
                <p className="text-[10px] uppercase tracking-[0.24em] text-[#8d6234]">Input</p>
                <h2 className="mt-2 text-[26px] leading-[1.02]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
                  Upscale Control Panel
                </h2>
              </div>
              <div className="rounded-xl border border-[#e3d4c2] bg-[#faf3ea] px-3 py-2 text-[11px] text-[#7a6046]">
                {loading ? "Processing" : "Ready"}
              </div>
            </div>

            <div className="grid gap-3">
              <label className="grid gap-2">
                <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">Source image</span>
                <input
                  className="rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 py-2 text-sm text-[#2f2419]"
                  type="file"
                  accept="image/*"
                  onChange={handleUpload}
                />
              </label>

              <div className="grid gap-3 md:grid-cols-2">
                <label className="grid gap-2">
                  <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">Model</span>
                  <select
                    className="h-11 rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 text-sm text-[#2f2419]"
                    value={model}
                    onChange={(event) => setModel(event.target.value as (typeof models)[number])}
                  >
                    {models.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2">
                  <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">Preset</span>
                  <select
                    className="h-11 rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 text-sm text-[#2f2419]"
                    value={preset}
                    onChange={(event) => setPreset(event.target.value as UpscalePreset)}
                  >
                    <option value="social_4k">Social 4K Master</option>
                    <option value="print_8k">Print 8K Final</option>
                  </select>
                </label>
              </div>

              <label className="grid gap-2">
                <span className="text-[11px] uppercase tracking-[0.18em] text-[#7b6249]">Enhance prompt</span>
                <textarea
                  className="min-h-[110px] rounded-xl border border-[#e2d1bc] bg-[#fcf8f2] px-3 py-2 text-sm text-[#2f2419]"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                />
              </label>
            </div>

            <div className="mt-5 flex flex-wrap gap-2.5">
              <button
                className="rounded-2xl bg-[#22170f] px-4 py-2.5 text-sm font-semibold text-[#f4e8d8] transition hover:bg-[#302117] md:px-5 md:py-3"
                type="button"
                onClick={runUpscale}
                disabled={loading}
              >
                {loading ? "Dang upscale..." : "Start Upscale"}
              </button>
            </div>

            {error ? (
              <div className="mt-4 rounded-xl border border-red-700/20 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}
          </div>

          <OperationFlowBridge sourceKey="upscale" title="UPSCALE OPERATION FLOW" theme="brand-studio" />
        </div>

        <div className="space-y-4 md:space-y-6">
          <div className="rounded-[22px] border border-[#d8c8b2] bg-[#20170f] p-5 text-[#f3e7d7] shadow-[0_20px_56px_rgba(22,12,5,0.22)] md:p-6 lg:p-7">
            <p className="text-[10px] uppercase tracking-[0.26em] text-[#d8b48a]">Preview</p>
            <h2
              className="mt-3 text-[30px] leading-[1.04] md:text-[38px] lg:text-[44px]"
              style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}
            >
              Before / After Upscale
            </h2>
            <p className="mt-3 text-[13px] leading-6 text-[#d9c6b1]">{resultSummary}</p>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <PreviewCard
                title="Source"
                subtitle={sourceFileName}
                imageSrc={sourceImageDataUrl}
                emptyText="Upload source image"
              />
              <PreviewCard
                title="Upscaled"
                subtitle={artifactImage?.artifactId || "No artifact image URL in response"}
                imageSrc={""}
                emptyText="Provider returns file artifact path on server"
              />
            </div>
          </div>

          <div className="rounded-[22px] border border-[#d8c8b2] bg-white p-5 shadow-[0_18px_40px_rgba(41,22,7,0.08)] md:p-6">
            <h3 className="text-[22px] leading-tight md:text-[24px]" style={{ fontFamily: "Fraunces, Playfair Display, Georgia, serif" }}>
              Upscale Job Timeline
            </h3>
            <div className="mt-4 grid gap-2">
              <TimelineItem label="Input ingest" state={sourceImageDataUrl ? "done" : "idle"} />
              <TimelineItem label="AI upscale refine" state={result ? "done" : loading ? "running" : "idle"} />
              <TimelineItem label="Artifact export" state={result?.artifacts?.length ? "done" : "idle"} />
            </div>

            <pre className="mt-4 max-h-[320px] overflow-auto rounded-2xl border border-[#e7d9c8] bg-[#f9f4ec] p-3 text-xs leading-6 text-[#5b4531]">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      </section>
    </main>
  );
}

function PreviewCard({
  title,
  subtitle,
  imageSrc,
  emptyText,
}: {
  title: string;
  subtitle: string;
  imageSrc: string;
  emptyText: string;
}) {
  return (
    <div className="rounded-2xl border border-[#4a3522] bg-[#2a1d12] p-3 md:p-4">
      <div className="text-[11px] uppercase tracking-[0.2em] text-[#c49a70]">{title}</div>
      <div className="mt-1 text-xs text-[#d9c6b1]">{subtitle}</div>
      <div className="mt-3 overflow-hidden rounded-xl border border-[#4a3522] bg-[#1b120b]">
        {imageSrc ? (
          <img className="h-[180px] w-full object-cover md:h-[220px]" src={imageSrc} alt={title} />
        ) : (
          <div className="flex h-[180px] items-center justify-center px-4 text-center text-xs text-[#c5ad92] md:h-[220px]">
            {emptyText}
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineItem({ label, state }: { label: string; state: "idle" | "running" | "done" }) {
  const styleMap = {
    idle: "border-[#d7c8b8] bg-[#faf2e8] text-[#7a6046]",
    running: "border-[#cfb28f] bg-[#fff4df] text-[#8a5f32]",
    done: "border-[#9cc6a2] bg-[#edf8ef] text-[#2f6940]",
  };

  return (
    <div className={`rounded-xl border px-3 py-2 text-sm ${styleMap[state]}`}>
      {label} · {state}
    </div>
  );
}
