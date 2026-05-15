"use client";

import { useState, useRef } from "react";

type Mode = "text_to_video" | "image_to_video";
type AspectRatio = "16:9" | "9:16";
type Duration = 4 | 6 | 8;
type Provider = "veo" | "kling" | "runway" | "seedance2";

interface ProviderResult {
  status: string;
  provider: string;
  account?: { email?: string };
  model: string;
  manifestPath?: string;
  operation?: unknown;
  note?: string;
  error?: string;
}

export default function ImageToVideoPanel() {
  const [provider, setProvider] = useState<Provider>("veo");
  const [mode, setMode] = useState<Mode>("image_to_video");
  const [prompt, setPrompt] = useState("");
  const [imageUri, setImageUri] = useState("");
  const [uploadedImageBase64, setUploadedImageBase64] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>("16:9");
  const [duration, setDuration] = useState<Duration>(6);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProviderResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const docInputRef = useRef<HTMLInputElement>(null);

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Chỉ chấp nhận JPEG, PNG hoặc WebP");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      setUploadedImageBase64(base64);
      setUploadedFileName(file.name);
      setImageUri(""); // clear URL input
      setError(null);
    };
    reader.onerror = () => setError("Lỗi đọc file ảnh");
    reader.readAsDataURL(file);
  }

  async function handleDocUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const isTxt = file.type === "text/plain" || file.name.endsWith(".txt");
    const isMd = file.name.endsWith(".md");
    const isDocx = file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || file.name.endsWith(".docx");

    if (!isTxt && !isMd && !isDocx) {
      setError("Chỉ chấp nhận .txt, .md hoặc .docx");
      return;
    }

    const reader = new FileReader();
    reader.onload = async () => {
      try {
        let extractedText = "";
        if (isTxt || isMd) {
          extractedText = reader.result as string;
        } else if (isDocx) {
          setError("Tạm thời chỉ hỗ trợ .txt và .md, vui lòng convert .docx thành .txt trước");
          return;
        }
        setPrompt(extractedText.trim());
        setUploadedFileName(file.name);
        setError(null);
      } catch (err) {
        setError("Lỗi đọc file tài liệu");
      }
    };
    reader.onerror = () => setError("Lỗi đọc file tài liệu");

    if (isTxt || isMd) {
      reader.readAsText(file);
    } else {
      reader.readAsArrayBuffer(file);
    }
  }

  function toRunwayRatio(value: AspectRatio) {
    return value === "16:9" ? "1280:720" : "720:1280";
  }

  function getProviderEndpoint(value: Provider) {
    if (value === "veo") return "/api/providers/google-managed/veo/generate";
    if (value === "kling") return "/api/providers/kling/generate";
    if (value === "runway") return "/api/providers/runway/generate";
    return "/api/providers/seedance2/generate";
  }

  function getProviderDisplay(value: Provider) {
    if (value === "veo") return "Google Veo 3.1";
    if (value === "kling") return "Kling";
    if (value === "runway") return "Runway";
    return "Seedance 2";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const finalImageUri = uploadedImageBase64 || (imageUri.trim() || undefined);
      const finalPrompt = prompt.trim();

      if (!finalPrompt) {
        throw new Error("Prompt không được để trống");
      }

      if (mode === "image_to_video" && !finalImageUri) {
        throw new Error("Chế độ ảnh → video cần ảnh hoặc URL ảnh");
      }

      const body: Record<string, unknown> = { prompt: finalPrompt };

      if (provider === "veo") {
        body.config = {
          aspectRatio,
          resolution: "1080p",
          durationSeconds: duration,
        };
        if (finalImageUri) body.imageUri = finalImageUri;
      } else if (provider === "kling") {
        body.durationSec = duration;
        body.aspectRatio = aspectRatio;
        if (finalImageUri) body.imageUri = finalImageUri;
      } else if (provider === "runway") {
        body.durationSec = duration;
        body.ratio = toRunwayRatio(aspectRatio);
        if (finalImageUri) body.imageUri = finalImageUri;
      } else {
        body.durationSec = duration;
        body.aspectRatio = aspectRatio;
        body.mode = mode;
        if (finalImageUri) body.imageUri = finalImageUri;
      }

      const res = await fetch(getProviderEndpoint(provider), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data: ProviderResult = await res.json();
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      {/* Mode toggle */}
      <div style={{ display: "flex", gap: "0.5rem" }}>
        {(["image_to_video", "text_to_video"] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            style={{
              padding: "0.4rem 1rem",
              borderRadius: "999px",
              border: "1px solid",
              borderColor: mode === m ? "#d4a843" : "#404040",
              background: mode === m ? "#d4a843" : "transparent",
              color: mode === m ? "#000" : "#ccc",
              fontWeight: mode === m ? 600 : 400,
              fontSize: "0.82rem",
              cursor: "pointer",
              transition: "all .15s",
            }}
          >
            {m === "image_to_video" ? "🖼 Ảnh → Video" : "✍ Text → Video"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1.25rem" }}>
        {/* Provider select */}
        <div style={{ display: "grid", gap: "0.4rem" }}>
          <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
            Video provider
          </label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value as Provider)}
            style={{
              background: "#111",
              border: "1px solid #333",
              borderRadius: "0.75rem",
              color: "#fff",
              padding: "0.55rem 0.9rem",
              fontSize: "0.9rem",
              outline: "none",
              cursor: "pointer",
            }}
          >
            <option value="veo">Google Veo 3.1</option>
            <option value="kling">Kling</option>
            <option value="runway">Runway</option>
            <option value="seedance2">Seedance 2</option>
          </select>
        </div>

        {/* Image URI input — only for image_to_video */}
        {mode === "image_to_video" && (
          <>
            <div style={{ display: "grid", gap: "0.4rem" }}>
              <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
                URL ảnh đầu vào <span style={{ color: "#666" }}>(GCS gs:// hoặc https://)</span>
              </label>
              <input
                type="url"
                value={imageUri}
                onChange={(e) => setImageUri(e.target.value)}
                placeholder="https://... hoặc gs://bucket/image.jpg"
                disabled={!!uploadedImageBase64}
                style={{
                  background: "#111",
                  border: "1px solid #333",
                  borderRadius: "0.75rem",
                  color: "#fff",
                  padding: "0.65rem 0.9rem",
                  fontSize: "0.9rem",
                  outline: "none",
                  width: "100%",
                  opacity: uploadedImageBase64 ? 0.5 : 1,
                }}
              />
            </div>

            <div style={{ display: "grid", gap: "0.4rem" }}>
              <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
                Hoặc tải ảnh từ thiết bị
              </label>
              <div
                onClick={() => imageInputRef.current?.click()}
                style={{
                  border: "2px dashed #333",
                  borderRadius: "0.75rem",
                  padding: "1.2rem",
                  textAlign: "center",
                  cursor: "pointer",
                  background: uploadedImageBase64 ? "#0d2018" : "#0a0a0f",
                  transition: "all .15s",
                }}
              >
                <input
                  ref={imageInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleImageUpload}
                  style={{ display: "none" }}
                />
                {uploadedImageBase64 ? (
                  <div style={{ color: "#4ade80", fontSize: "0.85rem" }}>
                    ✅ {uploadedFileName}
                  </div>
                ) : (
                  <div style={{ color: "#666", fontSize: "0.85rem", lineHeight: 1.5 }}>
                    Kéo/thả ảnh hoặc bấm để chọn<br/>
                    <span style={{ fontSize: "0.75rem" }}>JPEG, PNG, WebP</span>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Doc upload for text_to_video */}
        {mode === "text_to_video" && (
          <div style={{ display: "grid", gap: "0.4rem" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
              Hoặc tải file script: .txt, .md, .docx
            </label>
            <div
              onClick={() => docInputRef.current?.click()}
              style={{
                border: "2px dashed #333",
                borderRadius: "0.75rem",
                padding: "1.2rem",
                textAlign: "center",
                cursor: "pointer",
                background: uploadedFileName ? "#0d1618" : "#0a0a0f",
                transition: "all .15s",
              }}
            >
              <input
                ref={docInputRef}
                type="file"
                accept=".txt,.md,.docx"
                onChange={handleDocUpload}
                style={{ display: "none" }}
              />
              {uploadedFileName && mode === "text_to_video" ? (
                <div style={{ color: "#60a5fa", fontSize: "0.85rem" }}>
                  ✅ {uploadedFileName}
                </div>
              ) : (
                <div style={{ color: "#666", fontSize: "0.85rem", lineHeight: 1.5 }}>
                  Kéo/thả file hoặc bấm để chọn<br/>
                  <span style={{ fontSize: "0.75rem" }}>.txt, .md, .docx</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Prompt */}
        <div style={{ display: "grid", gap: "0.4rem" }}>
          <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
            Motion prompt
          </label>
          <textarea
            id="prompt-textarea"
            required
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={
              mode === "image_to_video"
                ? "Mô tả chuyển động mong muốn, ví dụ: slow zoom-in with golden light sweep..."
                : "Mô tả cảnh video đầy đủ, ánh sáng, chuyển động, cảm xúc..."
            }
            style={{
              background: "#111",
              border: "1px solid #333",
              borderRadius: "0.75rem",
              color: "#fff",
              padding: "0.65rem 0.9rem",
              fontSize: "0.9rem",
              outline: "none",
              resize: "vertical",
              width: "100%",
              fontFamily: "inherit",
            }}
          />
        </div>

        {/* Config row */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <div style={{ display: "grid", gap: "0.4rem", flex: "1 1 140px" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
              Tỉ lệ khung hình
            </label>
            <select
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value as AspectRatio)}
              style={{
                background: "#111",
                border: "1px solid #333",
                borderRadius: "0.75rem",
                color: "#fff",
                padding: "0.55rem 0.9rem",
                fontSize: "0.9rem",
                outline: "none",
                cursor: "pointer",
              }}
            >
              <option value="16:9">16:9 — Landscape</option>
              <option value="9:16">9:16 — Portrait / Reels</option>
            </select>
          </div>

          <div style={{ display: "grid", gap: "0.4rem", flex: "1 1 120px" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>
              Độ dài
            </label>
            <select
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value) as Duration)}
              style={{
                background: "#111",
                border: "1px solid #333",
                borderRadius: "0.75rem",
                color: "#fff",
                padding: "0.55rem 0.9rem",
                fontSize: "0.9rem",
                outline: "none",
                cursor: "pointer",
              }}
            >
              <option value={4}>4 giây</option>
              <option value={6}>6 giây</option>
              <option value={8}>8 giây</option>
            </select>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="brain-primary-btn"
          style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer" }}
        >
          {loading ? "Dang khoi tao render..." : `Render Video voi ${getProviderDisplay(provider)}`}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div
          style={{
            background: "#1a0a0a",
            border: "1px solid #7a2020",
            borderRadius: "0.75rem",
            padding: "0.85rem 1rem",
            color: "#f87171",
            fontSize: "0.88rem",
          }}
        >
          ⚠ {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div
          style={{
            background: "#0a1a0a",
            border: "1px solid #2a5a2a",
            borderRadius: "1rem",
            padding: "1.25rem",
            display: "grid",
            gap: "0.6rem",
          }}
        >
          <p style={{ color: "#4ade80", fontWeight: 700, fontSize: "0.95rem", margin: 0 }}>
            ✅ Operation khởi tạo thành công
          </p>
          <div style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", color: "#aaa" }}>
            <p style={{ margin: 0 }}>
              <span style={{ color: "#666" }}>Status:</span>{" "}
              <span style={{ color: "#fff" }}>{result.status}</span>
            </p>
            <p style={{ margin: 0 }}>
              <span style={{ color: "#666" }}>Provider:</span>{" "}
              <span style={{ color: "#fff" }}>{result.provider}</span>
            </p>
            <p style={{ margin: 0 }}>
              <span style={{ color: "#666" }}>Model:</span>{" "}
              <span style={{ color: "#fff" }}>{result.model}</span>
            </p>
            {result.account?.email && (
              <p style={{ margin: 0 }}>
                <span style={{ color: "#666" }}>Account:</span>{" "}
                <span style={{ color: "#fff" }}>{result.account.email}</span>
              </p>
            )}
            {result.manifestPath && (
              <p style={{ margin: 0 }}>
                <span style={{ color: "#666" }}>Manifest:</span>{" "}
                <code style={{ color: "#d4a843", fontSize: "0.82rem" }}>{result.manifestPath}</code>
              </p>
            )}
          </div>
          {result.note && (
            <p
              style={{
                margin: 0,
                padding: "0.6rem 0.9rem",
                background: "#111",
                borderRadius: "0.5rem",
                fontSize: "0.82rem",
                color: "#888",
              }}
            >
              ℹ {result.note}
            </p>
          )}
          <details style={{ marginTop: "0.25rem" }}>
            <summary style={{ fontSize: "0.8rem", color: "#555", cursor: "pointer" }}>
              Raw operation JSON
            </summary>
            <pre
              style={{
                marginTop: "0.5rem",
                background: "#0d0d0d",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                fontSize: "0.75rem",
                color: "#666",
                overflowX: "auto",
                maxHeight: "240px",
              }}
            >
              {JSON.stringify(result.operation, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
