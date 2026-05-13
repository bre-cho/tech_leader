"use client";

import { useEffect, useState } from "react";

export default function OpenRouterSettingsPanel() {
  const [settings, setSettings] = useState<any>({});
  const [apiKey, setApiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("openai/gpt-4o-mini");
  const [siteUrl, setSiteUrl] = useState("");
  const [appTitle, setAppTitle] = useState("AI Creative OS");

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
    await fetch("/api/settings/openrouter", {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        apiKey: apiKey || undefined,
        selectedModel,
        siteUrl,
        appTitle,
        enabled: true
      })
    });
    setApiKey("");
    await load();
  }

  async function test() {
    const res = await fetch("/api/settings/openrouter/test", { method: "POST" });
    alert(JSON.stringify(await res.json(), null, 2));
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
        <button className="rounded-xl bg-white px-4 py-3 font-semibold text-black" onClick={save}>Save AI Engine</button>
        <button className="rounded-xl bg-neutral-800 px-4 py-3" onClick={test}>Test OpenRouter</button>
      </div>
      <pre className="mt-5 whitespace-pre-wrap rounded-2xl bg-neutral-950 p-4 text-sm text-neutral-300">{JSON.stringify(settings, null, 2)}</pre>
    </section>
  );
}
