"use client";

import { useEffect, useState } from "react";

type NanoAccount = {
  id: string;
  label: string;
  maskedApiKey: string;
  enabled: boolean;
  quotaWeight: number;
  lastHealthStatus?: "ok" | "failed" | "unknown";
  capabilities: string[];
};

type Rotation = {
  enabled: boolean;
  strategy: "round_robin" | "least_recent" | "weighted";
  perScene: boolean;
};

type NanoState = {
  accounts: NanoAccount[];
  rotation: Rotation;
};

const primaryButtonClass =
  "rounded-xl bg-white px-4 py-3 font-semibold text-black transition hover:bg-neutral-200 disabled:cursor-not-allowed disabled:bg-neutral-500 disabled:text-neutral-900";
const secondaryButtonClass =
  "rounded-xl border border-neutral-700 bg-neutral-800 px-4 py-3 text-neutral-100 transition hover:border-neutral-500 hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-60";

export default function NanoBananaAccountsPanel() {
  const [state, setState] = useState<NanoState>({
    accounts: [],
    rotation: { enabled: false, strategy: "round_robin", perScene: true },
  });
  const [form, setForm] = useState({ label: "", apiKey: "", quotaWeight: 1 });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const response = await fetch("/api/settings/google-nanobanana", { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload?.error || "Cannot load NanoBanana accounts.");
    }
    setState(payload);
  }

  useEffect(() => {
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        await load();
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Cannot load NanoBanana accounts.";
        setError(message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function addAccount() {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const response = await fetch("/api/settings/google-nanobanana", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label: form.label,
          apiKey: form.apiKey,
          enabled: true,
          quotaWeight: Number(form.quotaWeight) || 1,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Cannot add NanoBanana account.");
      }
      setForm({ label: "", apiKey: "", quotaWeight: 1 });
      await load();
      setStatus("Added NanoBanana account.");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Cannot add NanoBanana account.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function removeAccount(id: string) {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const response = await fetch(`/api/settings/google-nanobanana/${id}`, { method: "DELETE" });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Cannot remove account.");
      }
      await load();
      setStatus("Removed account.");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Cannot remove account.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshAccount(id: string) {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const response = await fetch(`/api/settings/google-nanobanana/${id}/refresh`, { method: "POST" });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Cannot refresh account.");
      }
      await load();
      setStatus(`Health check: ${payload.status || "ok"}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Cannot refresh account.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function toggleEnabled(account: NanoAccount) {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const response = await fetch(`/api/settings/google-nanobanana/${account.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !account.enabled }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Cannot update account state.");
      }
      await load();
      setStatus(`Account ${payload.enabled ? "enabled" : "disabled"}.`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Cannot update account state.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function updateRotation(next: Rotation) {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const response = await fetch("/api/settings/google-nanobanana/rotation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error || "Cannot update rotation.");
      }
      await load();
      setStatus("Rotation updated.");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Cannot update rotation.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mt-6 rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
      <h2 className="text-2xl font-bold">Google NanoBanana Accounts</h2>
      <p className="mt-2 text-neutral-300">
        Manage NanoBanana API keys with rotation and health checks.
      </p>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <input
          className="rounded-xl bg-neutral-800 p-3"
          placeholder="Account label"
          value={form.label}
          onChange={(event) => setForm((current) => ({ ...current, label: event.target.value }))}
        />
        <input
          className="rounded-xl bg-neutral-800 p-3"
          placeholder="NanoBanana API key"
          value={form.apiKey}
          onChange={(event) => setForm((current) => ({ ...current, apiKey: event.target.value }))}
        />
        <input
          className="rounded-xl bg-neutral-800 p-3"
          placeholder="Quota weight"
          type="number"
          min={1}
          max={100}
          value={form.quotaWeight}
          onChange={(event) =>
            setForm((current) => ({ ...current, quotaWeight: Number(event.target.value) || 1 }))
          }
        />
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className={primaryButtonClass} onClick={addAccount} disabled={loading || !form.label || !form.apiKey}>
          Add NanoBanana Account
        </button>
        <button
          className={secondaryButtonClass}
          onClick={() => updateRotation({ ...state.rotation, enabled: !state.rotation.enabled })}
          disabled={loading}
        >
          Rotation: {state.rotation.enabled ? "ON" : "OFF"}
        </button>
        <button
          className={secondaryButtonClass}
          onClick={() => updateRotation({ ...state.rotation, perScene: !state.rotation.perScene })}
          disabled={loading}
        >
          Per Scene: {state.rotation.perScene ? "ON" : "OFF"}
        </button>
      </div>

      {status ? <div className="mt-4 rounded-xl border border-emerald-600/40 bg-emerald-950/40 p-3 text-sm text-emerald-300">{status}</div> : null}
      {error ? <div className="mt-4 rounded-xl border border-red-600/40 bg-red-950/40 p-3 text-sm text-red-300">{error}</div> : null}

      <div className="mt-5 grid gap-3">
        {state.accounts.map((account) => (
          <div key={account.id} className="rounded-2xl border border-neutral-700 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="font-semibold">{account.label}</div>
                <div className="text-sm text-neutral-400">
                  {account.maskedApiKey} · health: {account.lastHealthStatus || "unknown"} · quota: {account.quotaWeight}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button className={secondaryButtonClass} onClick={() => refreshAccount(account.id)} disabled={loading}>
                  Refresh
                </button>
                <button className={secondaryButtonClass} onClick={() => toggleEnabled(account)} disabled={loading}>
                  {account.enabled ? "Disable" : "Enable"}
                </button>
                <button
                  className="rounded-xl border border-red-700 bg-red-950 px-4 py-3 text-red-200 transition hover:bg-red-900 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={() => removeAccount(account.id)}
                  disabled={loading}
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}

        {!state.accounts.length ? (
          <div className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4 text-sm text-neutral-400">
            No NanoBanana account configured yet.
          </div>
        ) : null}
      </div>
    </section>
  );
}
