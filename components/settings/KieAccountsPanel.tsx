"use client";

import { useEffect, useState } from "react";

type KieAccount = {
  id: string;
  label: string;
  maskedApiKey: string;
  enabled: boolean;
  lastHealthStatus: "ok" | "failed" | "unknown";
  failCount: number;
  createdAt: string;
  updatedAt: string;
};

export default function KieAccountsPanel() {
  const [accounts, setAccounts] = useState<KieAccount[]>([]);
  const [label, setLabel] = useState("KIE Account 1");
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [testingId, setTestingId] = useState<string | null>(null);

  const primaryButtonClass =
    "rounded-xl bg-white px-4 py-3 font-semibold text-black transition hover:bg-neutral-200 disabled:cursor-not-allowed disabled:bg-neutral-500 disabled:text-neutral-900";
  const secondaryButtonClass =
    "rounded-xl border border-neutral-700 bg-neutral-800 px-4 py-3 text-neutral-100 transition hover:border-neutral-500 hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-60";

  async function load() {
    const res = await fetch("/api/settings/kie-accounts");
    if (res.ok) {
      const data = await res.json();
      setAccounts(Array.isArray(data) ? data : []);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function add() {
    if (!apiKey.trim()) {
      setError("API key is required.");
      return;
    }
    setSaving(true);
    setError(null);
    setStatus(null);
    try {
      const res = await fetch("/api/settings/kie-accounts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label: label.trim(), apiKey: apiKey.trim(), enabled: true }),
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload?.error || "Save failed.");
      setApiKey("");
      setLabel("KIE Account 1");
      setStatus("KIE account saved.");
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(id: string) {
    const res = await fetch(`/api/settings/kie-accounts/${id}`, { method: "DELETE" });
    if (res.ok) {
      setStatus("Account removed.");
      await load();
    }
  }

  async function testConnection(id: string) {
    setTestingId(id);
    setStatus(null);
    setError(null);
    try {
      const res = await fetch(`/api/settings/kie-accounts/${id}/test-connection`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.success) {
        setStatus(`Connection OK — kie.ai API key is valid.`);
      } else {
        setError(`Connection failed (${data.status ?? "?"}): ${data.detail ?? data.error ?? "unknown"}`);
      }
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Network error.");
    } finally {
      setTestingId(null);
    }
  }

  function healthBadge(status: KieAccount["lastHealthStatus"]) {
    const map = {
      ok: "bg-green-500/20 text-green-400",
      failed: "bg-red-500/20 text-red-400",
      unknown: "bg-neutral-700 text-neutral-400",
    };
    return (
      <span className={`rounded px-2 py-0.5 text-xs font-mono ${map[status]}`}>{status}</span>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-1 text-sm font-semibold text-white">
          Bytedance Seedance 2.0 — KIE API Key
        </h3>
        <p className="mb-4 text-xs text-neutral-400">
          Get your API key from{" "}
          <a
            href="https://kie.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-white"
          >
            kie.ai
          </a>
          . Docs:{" "}
          <a
            href="https://docs.kie.ai/market/bytedance/seedance-2"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-white"
          >
            Seedance 2 API reference
          </a>
          .
        </p>
      </div>

      {/* Add account form */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-4 space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
          Add account
        </p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs text-neutral-400">Label</label>
            <input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 focus:outline-none focus:ring-1 focus:ring-white"
              placeholder="KIE Account 1"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-neutral-400">API Key</label>
            <input
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              type="password"
              className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 focus:outline-none focus:ring-1 focus:ring-white"
              placeholder="sk-kie-..."
            />
          </div>
        </div>
        <button
          onClick={add}
          disabled={saving}
          className={primaryButtonClass}
        >
          {saving ? "Saving…" : "Save KIE Key"}
        </button>
      </div>

      {/* Feedback */}
      {status && (
        <p className="rounded-xl bg-green-900/30 px-4 py-2 text-sm text-green-400">{status}</p>
      )}
      {error && (
        <p className="rounded-xl bg-red-900/30 px-4 py-2 text-sm text-red-400">{error}</p>
      )}

      {/* Accounts list */}
      {accounts.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
            Saved accounts
          </p>
          {accounts.map((acc) => (
            <div
              key={acc.id}
              className="flex items-center justify-between rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-3"
            >
              <div>
                <p className="text-sm font-medium text-white">{acc.label}</p>
                <p className="font-mono text-xs text-neutral-500">{acc.maskedApiKey}</p>
                <div className="mt-1 flex items-center gap-2">
                  {healthBadge(acc.lastHealthStatus)}
                  {acc.failCount > 0 && (
                    <span className="text-xs text-red-400">fails: {acc.failCount}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => testConnection(acc.id)}
                  disabled={testingId === acc.id}
                  className={secondaryButtonClass + " text-sm"}
                >
                  {testingId === acc.id ? "Testing…" : "Test"}
                </button>
                <button
                  onClick={() => remove(acc.id)}
                  className="rounded-xl border border-red-800/50 bg-red-900/20 px-4 py-3 text-sm text-red-400 hover:bg-red-900/40"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {accounts.length === 0 && (
        <p className="text-center text-sm text-neutral-600">No KIE accounts saved yet.</p>
      )}
    </div>
  );
}
