"use client";

import { useState, useRef } from "react";
import SalesEngineV3Panel from "@/components/storyboard-v30/SalesEngineV3Panel";

export default function StoryboardV30Studio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [imageName, setImageName] = useState<string | null>(null);
  const [productImageBase64, setProductImageBase64] = useState<string | null>(null);
  const [productImageName, setProductImageName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const productInputRef = useRef<HTMLInputElement>(null);

  function makeUploadHandler(
    setter: (v: string) => void,
    nameSetter: (v: string) => void
  ) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        setUploadError("Chỉ chấp nhận JPEG, PNG hoặc WebP");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        setter(reader.result as string);
        nameSetter(file.name);
        setUploadError(null);
      };
      reader.onerror = () => setUploadError("Lỗi đọc file ảnh");
      reader.readAsDataURL(file);
    };
  }

  async function run() {
    setLoading(true);
    const res = await fetch("/api/storyboard/v30/sales-run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        title: "London Fashion Week — 160 Shot Fashion Film",
        format: "fashion_runway",
        mainCharacter: "1 cô gái / female model",
        location: "London Fashion Week",
        aspectRatio: "1:1",
        totalShots: 160,
        targetDurationSec: 240,
        requestedPhases: ["setup", "backstage", "runway", "after_party"],
        identityDna: {
          faceLock: true,
          wardrobeContinuity: true,
          hairMakeupContinuity: true,
          characterNotes: "same female fashion model, cinematic editorial beauty identity, confident runway persona"
        },
        providers: {
          still: "hidream",
          video: "veo",
          motionAlt: "runway"
        },
        outputDir: "storage/v30-storyboard-agent/demo",
        ...(imageBase64 ? { imageRef: imageBase64 } : {}),
        salesEngine: {
          enabled: true,
          productName: "son môi đỏ luxury Dior/YSL",
          category: "lipstick",
          brief: "Micro contrast on lips + lipstick only, eye highlight boost nhẹ, skin matte, lipstick touching lips",
          duration: 15,
          platform: "shorts",
          aspectRatio: "9:16",
          language: "vi",
          preserveIdentity: true,
          preserveProductShape: true,
          goal: "sale",
          ...(productImageBase64 ? { productImageRef: productImageBase64 } : {})
        }
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  const shots = result?.phases?.flatMap((p: any) => p.shots) ?? [];

  return (
    <main className="brain-route-main">
      <section className="brain-route-wrap">
        <div className="brain-route-head">
          <p className="brain-route-kicker">V30 Runtime</p>
          <h1 className="brain-route-title">Storyboard Agent: London Fashion Week</h1>
          <p className="brain-route-desc">Phase-aware 160-shot fashion event storyboard: Setup to Backstage to Runway to After Party.</p>

          {/* Upload row */}
          <div style={{ marginTop: "1.25rem", display: "grid", gap: "0.75rem", gridTemplateColumns: "1fr 1fr", maxWidth: "620px" }}>
            {/* Character image */}
            <div style={{ display: "grid", gap: "0.4rem" }}>
              <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>Ảnh nhân vật</label>
              <div
                onClick={() => imageInputRef.current?.click()}
                style={{
                  border: "2px dashed #333", borderRadius: "0.75rem", padding: "0.85rem",
                  cursor: "pointer", background: imageBase64 ? "#0d2018" : "#0a0a0f",
                  display: "flex", alignItems: "center", gap: "0.6rem", transition: "all .15s",
                }}
              >
                <input ref={imageInputRef} type="file" accept="image/jpeg,image/png,image/webp"
                  onChange={makeUploadHandler(setImageBase64, setImageName)} style={{ display: "none" }} />
                {imageBase64 ? (
                  <>
                    <img src={imageBase64} alt="preview" style={{ width: 40, height: 40, borderRadius: "0.4rem", objectFit: "cover" }} />
                    <p style={{ margin: 0, color: "#4ade80", fontSize: "0.8rem", fontWeight: 600 }}>✅ {imageName}</p>
                  </>
                ) : (
                  <p style={{ margin: 0, color: "#666", fontSize: "0.82rem", lineHeight: 1.4 }}>📸 Tải ảnh nhân vật<br /><span style={{ fontSize: "0.73rem" }}>JPEG, PNG, WebP</span></p>
                )}
              </div>
            </div>

            {/* Product image */}
            <div style={{ display: "grid", gap: "0.4rem" }}>
              <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>Ảnh sản phẩm</label>
              <div
                onClick={() => productInputRef.current?.click()}
                style={{
                  border: "2px dashed #333", borderRadius: "0.75rem", padding: "0.85rem",
                  cursor: "pointer", background: productImageBase64 ? "#0d1820" : "#0a0a0f",
                  display: "flex", alignItems: "center", gap: "0.6rem", transition: "all .15s",
                }}
              >
                <input ref={productInputRef} type="file" accept="image/jpeg,image/png,image/webp"
                  onChange={makeUploadHandler(setProductImageBase64, setProductImageName)} style={{ display: "none" }} />
                {productImageBase64 ? (
                  <>
                    <img src={productImageBase64} alt="product preview" style={{ width: 40, height: 40, borderRadius: "0.4rem", objectFit: "cover" }} />
                    <p style={{ margin: 0, color: "#60a5fa", fontSize: "0.8rem", fontWeight: 600 }}>✅ {productImageName}</p>
                  </>
                ) : (
                  <p style={{ margin: 0, color: "#666", fontSize: "0.82rem", lineHeight: 1.4 }}>🛍 Tải ảnh sản phẩm<br /><span style={{ fontSize: "0.73rem" }}>JPEG, PNG, WebP</span></p>
                )}
              </div>
            </div>
          </div>
          {uploadError && <p style={{ margin: "0.4rem 0 0 0", color: "#f87171", fontSize: "0.8rem" }}>⚠ {uploadError}</p>}

          <button onClick={run} disabled={loading} className="brain-primary-btn" style={{ marginTop: "1rem" }}>
            {loading ? "Đang dựng storyboard..." : "Run Storyboard Agent V30"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Analysis + Verification" data={{ analysis: result.analysis, verification: result.verification }} />
            <Panel title="Timeline" data={result.timeline} />
            <Panel title="Provider Batches" data={{
              stillItems: result.providerPayloads?.stillKeyframes?.items?.length,
              videoItems: result.providerPayloads?.videoShots?.items?.length,
              altMotionItems: result.providerPayloads?.altMotion?.items?.length,
              salesVideoItems: result.providerPayloads?.salesVideoShots?.items?.length,
              salesKeyframeItems: result.providerPayloads?.salesKeyframes?.items?.length
            }} />
            <SalesEngineV3Panel
              salesEngine={result.salesEngineV3}
              verification={result.verification}
              providerPayloads={result.providerPayloads}
            />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Shot List</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {shots.slice(0, 36).map((s: any) => (
                  <div key={s.id} className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
                    <div className="text-sm text-neutral-400">#{s.id} · {s.phase}</div>
                    <div className="font-semibold">{s.title}</div>
                    <div className="mt-2 text-sm text-neutral-300">{s.camera} · {s.movement}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

function Panel({ title, data }: { title: string; data: any }) {
  return (
    <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
      <h2 className="text-xl font-semibold">{title}</h2>
      <pre className="mt-3 max-h-[460px] overflow-auto whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
