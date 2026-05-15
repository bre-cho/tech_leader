"use client";

import { useState, useRef } from "react";

export default function StoryboardV31RhythmStudio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [imageName, setImageName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setUploadError("Chỉ chấp nhận JPEG, PNG hoặc WebP");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      setImageBase64(reader.result as string);
      setImageName(file.name);
      setUploadError(null);
    };
    reader.onerror = () => setUploadError("Lỗi đọc file ảnh");
    reader.readAsDataURL(file);
  }

  async function run() {
    setLoading(true);
    const res = await fetch("/api/storyboard/v31/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        title: "Fashion Shorts Rhythm Engine",
        concept: "London Fashion Week cinematic runway short",
        platform: "youtube_shorts",
        aspectRatio: "9:16",
        musicBpm: 118,
        targetDurationSec: 35,
        mainCharacter: "same female fashion model",
        location: "London Fashion Week",
        fashionDna: "luxury editorial runway, cinematic spotlight, confident model identity",
        provider: { image: "hidream", video: "veo", motionFallback: "runway" },
        outputDir: "storage/v31-storyboard-rhythm/demo",
        ...(imageBase64 ? { imageRef: imageBase64 } : {})
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="brain-route-main">
      <section className="brain-route-wrap">
        <div className="brain-route-head">
          <p className="brain-route-kicker">V31 Runtime</p>
          <h1 className="brain-route-title">Storyboard Retention and Rhythm Engine</h1>
          <p className="brain-route-desc">
            Rhythm graph, micro hooks, camera language, runway escalation, social proof, retention validation, and render queue.
          </p>

          {/* Image upload */}
          <div style={{ marginTop: "1.25rem", display: "grid", gap: "0.5rem" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
              Ảnh tham chiếu nhân vật / sản phẩm <span style={{ color: "#555" }}>(tùy chọn)</span>
            </label>
            <div
              onClick={() => imageInputRef.current?.click()}
              style={{
                border: "2px dashed #333",
                borderRadius: "0.75rem",
                padding: "1rem 1.25rem",
                cursor: "pointer",
                background: imageBase64 ? "#0d2018" : "#0a0a0f",
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                transition: "all .15s",
                maxWidth: "420px",
              }}
            >
              <input
                ref={imageInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleImageUpload}
                style={{ display: "none" }}
              />
              {imageBase64 ? (
                <>
                  <img src={imageBase64} alt="preview" style={{ width: 48, height: 48, borderRadius: "0.5rem", objectFit: "cover" }} />
                  <div>
                    <p style={{ margin: 0, color: "#4ade80", fontSize: "0.85rem", fontWeight: 600 }}>✅ {imageName}</p>
                    <p style={{ margin: 0, color: "#555", fontSize: "0.75rem" }}>Bấm để thay ảnh khác</p>
                  </div>
                </>
              ) : (
                <div style={{ color: "#666", fontSize: "0.85rem", lineHeight: 1.5 }}>
                  📸 Kéo/thả hoặc bấm để chọn ảnh tham chiếu<br />
                  <span style={{ fontSize: "0.75rem" }}>JPEG, PNG, WebP</span>
                </div>
              )}
            </div>
            {uploadError && <p style={{ margin: 0, color: "#f87171", fontSize: "0.8rem" }}>⚠ {uploadError}</p>}
          </div>

          <button onClick={run} disabled={loading} className="brain-primary-btn" style={{ marginTop: "1rem" }}>
            {loading ? "Đang tối ưu storyboard..." : "Run V31 Runtime"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Verification" data={result.verification} />
            <Panel title="Energy + Retention" data={{ energy: result.energyValidation, retention: result.retentionValidation, shortsTimeline: result.shortsTimeline }} />
            <Panel title="Optimization Engines" data={{ microHooks: result.microHooks, cameraLanguage: result.cameraLanguage, runwayEscalation: result.runwayEscalation, socialProof: result.socialProof }} />
            <Panel title="Provider Payload Summary" data={{ imageItems: result.providerPayloads?.imageKeyframes?.items?.length, videoItems: result.providerPayloads?.videoShots?.items?.length, renderQueue: result.providerPayloads?.renderQueue?.length }} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Rhythm Graph</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {result.rhythmGraph?.map((r: any) => (
                  <div key={r.shotId} className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
                    <div className="text-sm text-neutral-400">Shot #{r.shotId} · {r.hookType}</div>
                    <div className="mt-2 text-sm">Energy {r.energy} · Motion {r.motion} · Face {r.facePriority} · Social {r.socialProof}</div>
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
