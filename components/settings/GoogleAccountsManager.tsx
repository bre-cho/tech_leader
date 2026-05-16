"use client";

import { useEffect, useState } from "react";

export default function GoogleAccountsManager() {
  const [state, setState] = useState<any>({ accounts: [], rotation: { enabled: false, strategy: "round_robin", perScene: true } });
  const [form, setForm] = useState({ label: "", apiKey: "", enabled: true, capabilities: ["nano_banana", "veo_3_1"], quotaWeight: 1 });

  async function load() {
    const res = await fetch("/api/settings/google-accounts");
    setState(await res.json());
  }

  useEffect(() => { load(); }, []);

  async function add() {
    await fetch("/api/settings/google-accounts", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(form)
    });
    setForm({ ...form, label: "", apiKey: "" });
    await load();
  }

  async function remove(id: string) {
    await fetch(`/api/settings/google-accounts/${id}`, { method: "DELETE" });
    await load();
  }

  async function refresh(id: string) {
    await fetch(`/api/settings/google-accounts/${id}/refresh`, { method: "POST" });
    await load();
  }

  async function setRotation(next: any) {
    await fetch("/api/settings/google-accounts/rotation", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(next)
    });
    await load();
  }

  return (
    <section className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
      <h2 className="text-2xl font-bold">Manage Google Accounts</h2>
      <p className="mt-2 text-neutral-300">Add, remove, or refresh Google AI accounts. Enable Account Rotation to auto-cycle per scene for Nano Banana and Veo 3.1.</p>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="Account label" value={form.label} onChange={e => setForm({...form, label: e.target.value})} />
        <input className="rounded-xl bg-neutral-800 p-3" placeholder="Gemini API key" value={form.apiKey} onChange={e => setForm({...form, apiKey: e.target.value})} />
        <button className="btn-primary" onClick={add}>Add Account</button>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button className="btn-secondary" onClick={() => setRotation({...state.rotation, enabled: !state.rotation.enabled})}>
          Rotation: {state.rotation.enabled ? "ON" : "OFF"}
        </button>
        <button className="btn-secondary" onClick={() => setRotation({...state.rotation, perScene: !state.rotation.perScene})}>
          Per Scene: {state.rotation.perScene ? "ON" : "OFF"}
        </button>
      </div>

      <div className="mt-5 grid gap-3">
        {state.accounts.map((a: any) => (
          <div key={a.id} className="rounded-2xl border border-neutral-700 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-semibold">{a.label}</div>
                <div className="text-sm text-neutral-400">{a.maskedApiKey} · {a.capabilities.join(", ")} · health: {a.lastHealthStatus}</div>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary" onClick={() => refresh(a.id)}>Refresh</button>
                <button className="btn-danger" onClick={() => remove(a.id)}>Remove</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
