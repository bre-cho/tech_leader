"use client";

import ImageToVideoPanel from "@/components/video-render/ImageToVideoPanel";
import PromptTemplatesPanel from "@/components/video-render/PromptTemplatesPanel";

const PROVIDER_COMPARISON = [
  {
    name: "Google Veo 3.1",
    speed: "~60-120s",
    quality: "⭐⭐⭐⭐⭐",
    price: "Managed accounts",
    modes: "Text2V, Img2V, Keyframes",
    best: "Cinematic, editorial"
  },
  {
    name: "Kling",
    speed: "~30-60s",
    quality: "⭐⭐⭐⭐",
    price: "API key",
    modes: "Text2V, Img2V",
    best: "Social shorts, fast"
  },
  {
    name: "Runway",
    speed: "~45-90s",
    quality: "⭐⭐⭐⭐",
    price: "API key",
    modes: "Img2V (primary)",
    best: "Image motion, smooth flow"
  },
  {
    name: "Seedance 2",
    speed: "~30-75s",
    quality: "⭐⭐⭐⭐",
    price: "API key",
    modes: "Text2V, Img2V",
    best: "Flexible, diverse"
  }
];

export default function VideoRenderPage() {
  return (
    <main className="brain-route-main">
      <div className="brain-route-wrap">
        <section className="brain-route-head">
          <p className="brain-route-kicker">Video Generation</p>
          <h1 className="brain-route-title">Render Ảnh → Video</h1>
          <p className="brain-route-desc">
            Chuyển đổi ảnh tĩnh hoặc text prompt thành video chất lượng cao với Veo 3.1, Kling, Runway và Seedance2 ngay trên một form.
          </p>
        </section>

        <div
          style={{
            background: "#0f0f0f",
            border: "1px solid #1e1e1e",
            borderRadius: "1.25rem",
            padding: "1.75rem",
          }}
        >
          <ImageToVideoPanel />
        </div>

        {/* Provider Comparison Section */}
        <section
          style={{
            background: "#0a0a0f",
            border: "1px solid #1a1a2e",
            borderRadius: "1rem",
            padding: "1.25rem 1.5rem",
          }}
        >
          <p className="brain-route-kicker" style={{ marginBottom: "0.75rem" }}>
            So sánh Provider
          </p>
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                fontSize: "0.8rem",
                borderCollapse: "collapse",
                color: "#aaa",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "1px solid #222" }}>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#d4a843" }}>Provider</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#d4a843" }}>Tốc độ</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#d4a843" }}>Chất lượng</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#d4a843" }}>Modes</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#d4a843" }}>Phù hợp</th>
                </tr>
              </thead>
              <tbody>
                {PROVIDER_COMPARISON.map((p, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #111" }}>
                    <td style={{ padding: "0.5rem", color: "#fff" }}>{p.name}</td>
                    <td style={{ padding: "0.5rem" }}>{p.speed}</td>
                    <td style={{ padding: "0.5rem" }}>{p.quality}</td>
                    <td style={{ padding: "0.5rem", fontSize: "0.75rem" }}>{p.modes}</td>
                    <td style={{ padding: "0.5rem" }}>{p.best}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Prompt Templates Section */}
        <section
          style={{
            background: "#0a0a0f",
            border: "1px solid #1a1a2e",
            borderRadius: "1rem",
            padding: "1.25rem 1.5rem",
          }}
        >
          <p className="brain-route-kicker" style={{ marginBottom: "0.75rem" }}>
            Mẫu Prompt
          </p>
          <PromptTemplatesPanel />
        </section>

        {/* Recent Jobs Section */}
        <section
          style={{
            background: "#0a0a0f",
            border: "1px solid #1a1a2e",
            borderRadius: "1rem",
            padding: "1.25rem 1.5rem",
          }}
        >
          <p className="brain-route-kicker" style={{ marginBottom: "0.75rem" }}>
            Job gần đây
          </p>
          <div style={{ display: "grid", gap: "0.5rem", fontSize: "0.85rem", color: "#777" }}>
            <p style={{ margin: 0, color: "#555" }}>
              Khi chạy render, job sẽ được lưu tại <code style={{ color: "#d4a843", fontSize: "0.8rem" }}>storage/*/operation_*.json</code>
            </p>
            <p style={{ margin: 0, color: "#555" }}>
              Kiểm tra manifest để theo dõi tiến trình provider và lấy artifact video hoàn thiện.
            </p>
            <div
              style={{
                background: "#0d0d0d",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                color: "#666",
                fontSize: "0.8rem",
              }}
            >
              <strong style={{ color: "#888" }}>Paths:</strong>
              <ul style={{ margin: "0.4rem 0 0 1.2rem", paddingLeft: 0 }}>
                <li>Veo: storage/veo-managed/</li>
                <li>Kling: storage/kling-managed/</li>
                <li>Runway: storage/runway-managed/</li>
                <li>Seedance2: storage/seedance2-managed/</li>
              </ul>
            </div>
          </div>
        </section>

        <section
          style={{
            background: "#0a0a0f",
            border: "1px solid #1a1a2e",
            borderRadius: "1rem",
            padding: "1.25rem 1.5rem",
          }}
        >
          <p className="brain-route-kicker" style={{ marginBottom: "0.75rem" }}>
            Hướng dẫn
          </p>
          <ul
            style={{
              margin: 0,
              paddingLeft: "1.25rem",
              display: "grid",
              gap: "0.4rem",
              fontSize: "0.875rem",
              color: "#777",
              lineHeight: 1.6,
            }}
          >
            <li>
              <strong style={{ color: "#aaa" }}>Ảnh → Video:</strong> tải ảnh từ thiết bị hoặc dán URL (GCS{" "}
              <code style={{ fontSize: "0.8rem", color: "#d4a843" }}>gs://</code> / https://) + motion prompt.
            </li>
            <li>
              <strong style={{ color: "#aaa" }}>Text → Video:</strong> dán prompt hoặc tải script .txt / .md để extract nội dung tự động.
            </li>
            <li>
              <strong style={{ color: "#aaa" }}>Provider:</strong> chọn từ dropdown — Veo 3.1 (ổn định), Kling (nhanh), Runway (hình ảnh động), Seedance2 (linh hoạt).
            </li>
            <li>
              Operation được khởi tạo bất đồng bộ — manifest JSON lưu theo provider tại{" "}
              <code style={{ fontSize: "0.8rem", color: "#d4a843" }}>storage/*-managed/</code>.
            </li>
            <li>
              Quản lý key/account tại{" "}
              <a href="/settings/ai-engine" style={{ color: "#d4a843", textDecoration: "none" }}>
                Settings → AI Engine
              </a>
              .
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}
