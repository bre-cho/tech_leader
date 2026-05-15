"use client";

import { useEffect, useState } from "react";

export default function OpenRouterSettingsPanel() {
  const [settings, setSettings] = useState<any>({});
  const [apiKey, setApiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("openai/gpt-4o-mini");
  const [siteUrl, setSiteUrl] = useState("");
  const [appTitle, setAppTitle] = useState("AI Creative OS");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const primaryButtonClass =
    "rounded-xl bg-white px-4 py-3 font-semibold text-black transition hover:bg-neutral-200 disabled:cursor-not-allowed disabled:bg-neutral-500 disabled:text-neutral-900";
  const secondaryButtonClass =
    "rounded-xl border border-neutral-700 bg-neutral-800 px-4 py-3 text-neutral-100 transition hover:border-neutral-500 hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-60";

  function normalizeSiteUrl(value: string): string {
    const trimmed = value.trim();
    if (!trimmed) {
      return "";
    }
    if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
      return trimmed;
    }
    return `https://${trimmed}`;
  }

  async function load() {
    const res = await fetch("/api/settings/openrouter");
    const data = await res.json();
    setSettings(data);
    if (data.selectedModel) setSelectedModel(data.selectedModel);
    if (data.siteUrl) setSiteUrl(data.siteUrl);
    if (data.appTitle) setAppTitle(data.appTitle);
  }

  useEffect(() => { load(); }, []);

  async function save() {
    setSaving(true);
    setError(null);
    setStatus(null);
    try {
      const response = await fetch("/api/settings/openrouter", {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          apiKey: apiKey || undefined,
          selectedModel,
          siteUrl: normalizeSiteUrl(siteUrl),
          appTitle,
          enabled: true
        })
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Save failed.");
      }

      setApiKey("");
      setStatus("Saved AI Engine settings successfully.");
      await load();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Save failed.";
      setError(message);
    } finally {
      setSaving(false);
    }
  }

  async function test() {
    setTesting(true);
    setError(null);
    setStatus(null);
    setTestResult(null);
    try {
      const res = await fetch("/api/settings/openrouter/test", { method: "POST" });
      const payload = await res.json();
      setTestResult(payload);
      if (!res.ok) {
        throw new Error(payload?.error || "OpenRouter test failed.");
      }
      setStatus("OpenRouter test succeeded.");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "OpenRouter test failed.";
      setError(message);
    } finally {
      setTesting(false);
    }
  }

  return (
    <section className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
      <h2 className="text-2xl font-bold">Settings → AI Engine</h2>
      <p className="mt-2 text-neutral-300">Update OpenRouter key or switch AI models. Keys are stored encrypted server-side.</p>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="OpenRouter API key" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="Model, e.g. openai/gpt-4o-mini" value={selectedModel} onChange={e => setSelectedModel(e.target.value)} />
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="HTTP-Referer site URL" value={siteUrl} onChange={e => setSiteUrl(e.target.value)} />
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="X-Title app title" value={appTitle} onChange={e => setAppTitle(e.target.value)} />
      </div>
      <div className="mt-5 flex gap-3">
        <button className={primaryButtonClass} onClick={save} disabled={saving}>
          {saving ? "Saving..." : "Save AI Engine"}
        </button>
        <button className={secondaryButtonClass} onClick={test} disabled={testing}>
          {testing ? "Testing..." : "Test OpenRouter"}
        </button>
      </div>
      {status ? <div className="mt-4 rounded-xl border border-emerald-600/40 bg-emerald-950/40 p-3 text-sm text-emerald-300">{status}</div> : null}
      {error ? <div className="mt-4 rounded-xl border border-red-600/40 bg-red-950/40 p-3 text-sm text-red-300">{error}</div> : null}
      <pre className="mt-5 whitespace-pre-wrap rounded-2xl bg-neutral-950 p-4 text-sm text-neutral-300">{JSON.stringify(settings, null, 2)}</pre>
      {testResult ? (
        <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-neutral-950 p-4 text-sm text-neutral-300">{JSON.stringify(testResult, null, 2)}</pre>
      ) : null}
    </section>
  );
}
