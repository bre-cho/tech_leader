import { useEffect, useMemo, useState } from "react";
import { runDesignStudio } from "../lib/api";
import "../styles.css";

type Brief = {
  industry: string;
  product: string;
  audience: string;
  channel: string;
  goal: string;
  brandName: string;
  budgetTier: string;
  language: string;
};

type StudioResult = {
  plan?: any;
  best_concept?: any;
  storyboard?: any[];
  upsell?: any;
  offers?: any[];
  verification?: any;
  memory_update?: any;
  provider_job?: {
    job_id?: string;
    provider?: string;
    status?: string;
    preview_url?: string;
    metadata?: Record<string, any>;
  };
  [key: string]: any;
};

type PipelineHandoffPayload = {
  source?: string;
  workflowId?: string;
  createdAt?: string;
  request?: {
    storyboard?: Array<Record<string, any>>;
    [key: string]: any;
  };
  providerPayloadResult?: Record<string, any>;
  videoFlowCompile?: {
    status?: string;
    videoFlowTimeline?: {
      shots?: Array<Record<string, any>>;
      [key: string]: any;
    };
    [key: string]: any;
  };
  [key: string]: any;
};

const PIPELINE_HANDOFF_LATEST_KEY = "pipeline-os:v31-handoff:latest";
const PIPELINE_HANDOFF_SESSION_KEY = "pipeline-os:v31-handoff";

const lifecycleSteps = [
  { key: "target_define", label: "Xác định mục tiêu", desc: "Ngành, sản phẩm, khách hàng, kênh, mục tiêu" },
  { key: "research", label: "Nhớ lại mẫu thắng", desc: "Winner DNA + ngữ cảnh cũ" },
  { key: "plan", label: "Lập kế hoạch", desc: "Chiến lược nội dung và hướng triển khai" },
  { key: "concept", label: "Đấu ý tưởng", desc: "So sánh nhiều concept theo điểm số" },
  { key: "storyboard", label: "Storyboard", desc: "Chia cảnh, nhịp dựng, lời thoại" },
  { key: "verify", label: "Cổng kiểm duyệt", desc: "Kiểm tra tính đúng, đủ, sẵn sàng render" },
  { key: "memory", label: "Lưu trí nhớ thắng", desc: "Cập nhật Winner DNA" },
  { key: "provider", label: "Sẵn sàng render", desc: "Chuẩn bị Veo / Runway / Kling / Seedance" },
];

const agents = [
  "Strategy Agent",
  "Research Agent",
  "Concept Agent",
  "Storyboard Agent",
  "Offer Agent",
  "Verification Agent",
  "Memory Agent",
];

const defaultBrief: Brief = {
  industry: "Beauty / K-Beauty",
  product: "AI video campaign",
  audience: "Khách hàng nữ 18-34 yêu thích làm đẹp",
  channel: "TikTok / Reels / Shorts",
  goal: "Tăng chuyển đổi và ghi nhớ thương hiệu",
  brandName: "TUNGNS Studio",
  budgetTier: "medium",
  language: "vi",
};

function safeParseJson(raw: string | null): PipelineHandoffPayload | null {
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as PipelineHandoffPayload;
  } catch {
    return null;
  }
}

function parseHandoffFromQuery(raw: string | null): PipelineHandoffPayload | null {
  if (!raw) {
    return null;
  }

  const direct = safeParseJson(raw);
  if (direct) {
    return direct;
  }

  try {
    const decoded = atob(raw);
    return safeParseJson(decoded);
  } catch {
    return null;
  }
}

function readLatestHandoffFromStorage(): PipelineHandoffPayload | null {
  const fromSession = safeParseJson(sessionStorage.getItem(PIPELINE_HANDOFF_SESSION_KEY));
  if (fromSession) {
    localStorage.setItem(PIPELINE_HANDOFF_LATEST_KEY, JSON.stringify(fromSession));
    return fromSession;
  }

  const fromLocal = safeParseJson(localStorage.getItem(PIPELINE_HANDOFF_LATEST_KEY));
  if (fromLocal) {
    return fromLocal;
  }

  return null;
}

function getCompletion(result: StudioResult | null, key: string) {
  if (!result) return "idle";
  if (key === "target_define") return "done";
  if (key === "research" && (result.memory_update || result.plan)) return "done";
  if (key === "plan" && result.plan) return "done";
  if (key === "concept" && result.best_concept) return "done";
  if (key === "storyboard" && Array.isArray(result.storyboard)) return "done";
  if (key === "verify" && result.verification) return "done";
  if (key === "memory" && result.memory_update) return "done";
  if (key === "provider" && result.provider_job) return "done";
  return "pending";
}

function scoreFrom(value: any, fallback = 88) {
  if (!value) return fallback;
  return value.score || value.total_score || value.final_score || value.rank_score || fallback;
}

export default function DesignStudio() {
  const searchParams = useMemo(() => new URLSearchParams(window.location.search), []);
  const source = searchParams.get("source");
  const renderMode = searchParams.get("render");
  const handoffQuery = searchParams.get("handoff");

  const [brief, setBrief] = useState<Brief>(defaultBrief);
  const [result, setResult] = useState<StudioResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [handoffPayload, setHandoffPayload] = useState<PipelineHandoffPayload | null>(null);
  const [handoffError, setHandoffError] = useState<string | null>(null);

  const conceptScore = useMemo(() => scoreFrom(result?.best_concept, 0), [result]);
  const verificationScore = useMemo(() => scoreFrom(result?.verification, 0), [result]);

  useEffect(() => {
    if (source !== "pipeline-os") {
      return;
    }

    const fromQuery = parseHandoffFromQuery(handoffQuery);
    if (fromQuery) {
      setHandoffPayload(fromQuery);
      setHandoffError(null);
      localStorage.setItem(PIPELINE_HANDOFF_LATEST_KEY, JSON.stringify(fromQuery));
      return;
    }

    const fromStorage = readLatestHandoffFromStorage();
    if (fromStorage) {
      setHandoffPayload(fromStorage);
      setHandoffError(null);
      return;
    }

    setHandoffPayload(null);
    setHandoffError("Khong tim thay payload handoff. Hay mo lai tu trang Pipeline OS sau khi compile.");
  }, [handoffQuery, source]);

  const handoffScenes = useMemo(() => {
    if (!handoffPayload?.request?.storyboard || !Array.isArray(handoffPayload.request.storyboard)) {
      return [] as Array<Record<string, any>>;
    }
    return handoffPayload.request.storyboard;
  }, [handoffPayload]);

  const timelineShots = useMemo(() => {
    const shots = handoffPayload?.videoFlowCompile?.videoFlowTimeline?.shots;
    return Array.isArray(shots) ? shots : [];
  }, [handoffPayload]);

  if (source === "pipeline-os") {
    return (
      <main className="studio-page">
        <section className="studio-hero">
          <div>
            <p className="eyebrow">Pipeline OS Handoff</p>
            <h1>Realtime Video Render Console</h1>
            <p className="hero-copy">
              Che do render tu dong da kich hoat cho luong IMAGE - STORYBOARD - VIDEO.
              Du lieu ben duoi duoc nap tu payload handoff gan nhat cua Pipeline OS.
            </p>
          </div>
          <div className="hero-status-card">
            <span>Nguon</span>
            <strong>{source}</strong>
            <small>
              {renderMode === "video" ? "Render mode: video" : "Render mode: standard"}
            </small>
          </div>
        </section>

        <section className="delivery-grid handoff-runtime-grid">
          <div className="panel timeline-panel">
            <div className="panel-header horizontal">
              <div>
                <p className="eyebrow">Storyboard Input</p>
                <h2>Canh tu payload handoff</h2>
              </div>
              <span className="pill">{handoffScenes.length} canh</span>
            </div>

            {handoffError ? <p className="error-box">{handoffError}</p> : null}

            <div className="timeline-list">
              {handoffScenes.map((scene, index) => (
                <article className="scene-card" key={`${scene.scene_id || "scene"}-${index}`}>
                  <span>Canh {String(index + 1).padStart(2, "0")}</span>
                  <strong>{scene.title || scene.shot || scene.scene || "Untitled scene"}</strong>
                  <p>{scene.description || scene.prompt || scene.copy || "Khong co mo ta."}</p>
                </article>
              ))}
              {handoffScenes.length === 0 ? (
                <p className="empty-state">Chua co storyboard trong payload handoff.</p>
              ) : null}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <p className="eyebrow">Render Status</p>
              <h2>VideoFlow compile</h2>
            </div>
            <div className="gate-score">
              <strong>{handoffPayload?.videoFlowCompile?.status || "idle"}</strong>
              <span>trang thai compile</span>
            </div>
            <pre>
              {handoffPayload
                ? JSON.stringify(
                    {
                      workflowId: handoffPayload.workflowId,
                      createdAt: handoffPayload.createdAt,
                      compile: handoffPayload.videoFlowCompile,
                      providerPayload: handoffPayload.providerPayloadResult,
                    },
                    null,
                    2,
                  )
                : "Chua co payload handoff."}
            </pre>
          </div>

          <div className="panel">
            <div className="panel-header">
              <p className="eyebrow">Timeline Shots</p>
              <h2>Shot map de render</h2>
            </div>
            <div className="provider-grid">
              <span>Tong shot: {timelineShots.length}</span>
              <span>Workflow: {handoffPayload?.workflowId || "unknown"}</span>
            </div>
            <pre>{timelineShots.length > 0 ? JSON.stringify(timelineShots, null, 2) : "Chua co shots compile."}</pre>
          </div>
        </section>
      </main>
    );
  }

  const updateBrief = (field: keyof Brief, value: string) => {
    setBrief((current) => ({ ...current, [field]: value }));
  };

  const handleRun = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const payload = {
        industry: brief.industry,
        product: brief.product,
        audience: brief.audience,
        channel: brief.channel,
        goal: brief.goal,
        brand_name: brief.brandName,
        budget_tier: brief.budgetTier,
        language: brief.language,
      };
      const response = await runDesignStudio(payload);
      setResult(response);
    } catch (err: any) {
      setError(err?.message || "Không thể chạy Design Studio. Hãy kiểm tra API backend.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <main className="studio-page">
      <section className="studio-hero">
        <div>
          <p className="eyebrow">Realtime Design-to-Video Studio</p>
          <h1>Mission Control cho quy trình sản xuất video AI</h1>
          <p className="hero-copy">
            Biến brief thành kế hoạch, ý tưởng thắng, storyboard, cổng kiểm duyệt,
            trí nhớ Winner DNA và trạng thái sẵn sàng render qua provider.
          </p>
        </div>
        <div className="hero-status-card">
          <span>Trạng thái hệ thống</span>
          <strong>{isRunning ? "Đang điều phối" : result ? "Đã có kết quả" : "Sẵn sàng"}</strong>
          <small>Backend orchestration + agents + memory + provider runtime</small>
        </div>
      </section>

      <section className="mission-grid">
        <aside className="brief-card panel">
          <div className="panel-header">
            <p className="eyebrow">Creative Brief</p>
            <h2>Thông tin đầu vào</h2>
          </div>

          <div className="form-grid">
            <label>Ngành<input value={brief.industry} onChange={(e) => updateBrief("industry", e.target.value)} /></label>
            <label>Sản phẩm<input value={brief.product} onChange={(e) => updateBrief("product", e.target.value)} /></label>
            <label>Khách hàng<textarea value={brief.audience} onChange={(e) => updateBrief("audience", e.target.value)} /></label>
            <label>Kênh<input value={brief.channel} onChange={(e) => updateBrief("channel", e.target.value)} /></label>
            <label>Mục tiêu<textarea value={brief.goal} onChange={(e) => updateBrief("goal", e.target.value)} /></label>
            <label>Thương hiệu<input value={brief.brandName} onChange={(e) => updateBrief("brandName", e.target.value)} /></label>
            <label>Ngân sách<select value={brief.budgetTier} onChange={(e) => updateBrief("budgetTier", e.target.value)}><option value="low">low</option><option value="medium">medium</option><option value="high">high</option></select></label>
            <label>Ngôn ngữ<select value={brief.language} onChange={(e) => updateBrief("language", e.target.value)}><option value="vi">Tiếng Việt</option><option value="en">English</option></select></label>
          </div>

          <button className="primary-button" onClick={handleRun} disabled={isRunning}>
            {isRunning ? "Đang chạy vòng đời sản xuất..." : "Run Mission Control"}
          </button>
          {error && <p className="error-box">{error}</p>}
        </aside>

        <section className="control-stack">
          <div className="panel">
            <div className="panel-header horizontal">
              <div><p className="eyebrow">8-Step Lifecycle Graph</p><h2>Luồng sản xuất hoàn chỉnh</h2></div>
              <span className="pill">Không còn form → JSON</span>
            </div>
            <div className="lifecycle-grid">
              {lifecycleSteps.map((step, index) => (
                <div key={step.key} className={`lifecycle-node ${getCompletion(result, step.key)}`}>
                  <span className="node-index">{String(index + 1).padStart(2, "0")}</span>
                  <strong>{step.label}</strong>
                  <small>{step.desc}</small>
                </div>
              ))}
            </div>
          </div>

          <div className="runtime-grid">
            <div className="panel">
              <div className="panel-header"><p className="eyebrow">7-Agent Runtime</p><h2>Đội agent vận hành</h2></div>
              <div className="agent-list">
                {agents.map((agent, index) => <div className="agent-row" key={agent}><span>{agent}</span><b>{result ? "done" : index === 0 && isRunning ? "running" : "idle"}</b></div>)}
              </div>
            </div>

            <div className="panel scoring-card">
              <div className="panel-header"><p className="eyebrow">Concept Battle</p><h2>Điểm ý tưởng</h2></div>
              <div className="score-ring"><strong>{conceptScore || "--"}</strong><span>/100</span></div>
              <p>{result?.best_concept?.title || result?.best_concept?.name || "Chưa có concept thắng."}</p>
            </div>
          </div>
        </section>
      </section>

      <section className="delivery-grid">
        <div className="panel timeline-panel">
          <div className="panel-header horizontal"><div><p className="eyebrow">Storyboard Timeline</p><h2>Dòng thời gian cảnh quay</h2></div><span className="pill">{Array.isArray(result?.storyboard) ? `${result?.storyboard?.length} cảnh` : "Chưa tạo"}</span></div>
          <div className="timeline-list">
            {(result?.storyboard || []).slice(0, 12).map((scene: any, index: number) => (
              <article className="scene-card" key={index}>
                <span>Cảnh {String(index + 1).padStart(2, "0")}</span>
                <strong>{scene.title || scene.shot || scene.scene || "Untitled scene"}</strong>
                <p>{scene.description || scene.prompt || scene.copy || JSON.stringify(scene).slice(0, 180)}</p>
              </article>
            ))}
            {!result?.storyboard && <p className="empty-state">Storyboard sẽ xuất hiện ở đây sau khi chạy Mission Control.</p>}
          </div>
        </div>

        <div className="panel gate-panel">
          <div className="panel-header"><p className="eyebrow">Verification Gate</p><h2>Cổng kiểm duyệt</h2></div>
          <div className="gate-score"><strong>{verificationScore || "--"}</strong><span>điểm sẵn sàng</span></div>
          <pre>{result?.verification ? JSON.stringify(result.verification, null, 2) : "Chưa có dữ liệu kiểm duyệt."}</pre>
        </div>

        <div className="panel provider-panel">
          <div className="panel-header"><p className="eyebrow">Provider Runtime</p><h2>Sẵn sàng render</h2></div>
          <div className="provider-grid">
            {["Veo", "Runway", "Kling", "Seedance"].map((provider) => <span key={provider}>{provider}</span>)}
          </div>
          <pre>{result?.provider_job ? JSON.stringify(result.provider_job, null, 2) : "Backend cần trả provider_job: { job_id, provider, status, preview_url, metadata }."}</pre>
        </div>

        <div className="panel memory-panel">
          <div className="panel-header"><p className="eyebrow">Winner DNA Memory</p><h2>Trí nhớ chiến thắng</h2></div>
          <pre>{result?.memory_update ? JSON.stringify(result.memory_update, null, 2) : "Chưa có cập nhật trí nhớ."}</pre>
        </div>
      </section>
    </main>
  );
}
